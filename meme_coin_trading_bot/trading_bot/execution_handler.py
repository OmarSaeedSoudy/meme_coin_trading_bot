import os
import base64
import requests
import logging
import base58
from django.conf import settings
from solana.rpc.api import Client
from solders.transaction import Transaction
from solders.keypair import Keypair
import time
from datetime import timezone
from .models import Trades, MarketData
import dotenv

logger = logging.getLogger(__name__)

class ExecutionError(Exception):
    pass

class ExecutionHandler:
    def __init__(self):
        self.rpc_url = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
        self.rpc_client = Client(self.rpc_url)
        self.wallet = self._load_wallet()
        self.token_list = self._fetch_jupiter_token_list()
        self.jup_base = "https://quote-api.jup.ag/v6"

    def _load_wallet(self) -> Keypair:
        """Load wallet from environment variable"""
        privkey = os.getenv("Solana_Private_Key")
        if not privkey:
            raise ExecutionError("Missing SOLANA_PRIVATE_KEY in environment")

        try:
            return Keypair.from_bytes(base58.b58decode(privkey))
        except Exception as e:
            raise ExecutionError(f"Invalid private key: {str(e)}")

    def _fetch_jupiter_token_list_old(self) -> dict:
        """Fetch latest token list from Jupiter"""
        try:
            response = requests.get("https://token.jup.ag/api/tokens/")
            response.raise_for_status()
            return {t['symbol'].upper(): t for t in response.json()}
        except Exception as e:
            logger.error(f"Failed to fetch token list: {str(e)}")
            return {}

    def _fetch_jupiter_token_list(self) -> dict:
        """Fetch latest token list from Jupiter with proper error handling"""
        endpoints = [
            "https://token.jup.ag/v4/tokens",  # Current main endpoint
            "https://cache.jup.ag/tokens",     # Alternative cache endpoint
            "https://cdn.jsdelivr.net/gh/jup-ag/token-list@latest/tokens.json"  # Fallback
        ]

        for url in endpoints:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()

                # New response format validation
                tokens = response.json()
                if not isinstance(tokens, list) or len(tokens) == 0:
                    raise ValueError("Invalid token list format")

                # Use mint address as key to avoid symbol conflicts
                return {t['address']: t for t in tokens}

            except Exception as e:
                logger.warning(f"Failed with {url}: {str(e)}")
                continue

        logger.error("All Jupiter token list endpoints failed")
        return {}

    def _get_token_metadata(self, symbol: str) -> dict:
        """Get token mint address and decimals"""
        token = self.token_list.get(symbol.upper())
        if not token:
            raise ExecutionError(f"Token {symbol} not found in Jupiter registry")
        return {
            'mint': token['address'],
            'decimals': token['decimals']
        }

    def execute_buy_order(self, coin_symbol: str, usd_amount: float) -> Trades:
        """Execute buy order for a meme coin"""
        try:
            # Get current SOL price in USD
            sol_data = MarketData.objects.filter(coin_id="SOL").latest('last_updated')
            print("sol_data: ", sol_data)
            sol_price = float(sol_data.price)
            sol_amount = usd_amount / sol_price

            # Get token metadata
            token = self._get_token_metadata(coin_symbol)
            print("token: ", token)

            # Get Jupiter quote
            quote = self._get_quote(
                input_mint="So11111111111111111111111111111111111111112",  # SOL
                output_mint=token['mint'],
                amount=int(sol_amount * 1e9)  # SOL in lamports
            )

            # Execute swap
            tx_sig = self._execute_swap(quote)

            # Calculate token quantity
            token_amount = quote['outAmount'] / (10 ** token['decimals'])

            # Create trade record
            return Trades.objects.create(
                coin_id=coin_symbol,
                trade_type="BUY",
                buying_price=usd_amount / token_amount,  # USD per token
                quantity=token_amount,
                total_paid_amount=usd_amount,
                tx_hash=tx_sig,
                wallet_address=str(self.wallet.pubkey()),
                token_address=token['mint'],
                status="OPEN"
            )
        except Exception as e:
            logger.error(f"Buy order failed: {str(e)}")
            raise ExecutionError(f"Buy execution failed: {str(e)}")

    def execute_sell_order(self, trade: Trades) -> Trades:
        """Execute sell order for an existing position"""
        try:
            # Get token metadata
            token = self._get_token_metadata(trade.coin_id)

            # Get Jupiter quote
            quote = self._get_quote(
                input_mint=token['mint'],
                output_mint="So11111111111111111111111111111111111111112",  # SOL
                amount=int(trade.quantity * (10 ** token['decimals']))
            )

            # Execute swap
            tx_sig = self._execute_swap(quote)

            # Get current SOL price
            sol_data = MarketData.objects.filter(coin_id="SOL").latest('last_updated')
            sol_price = float(sol_data.price)
            received_usd = (quote['outAmount'] / 1e9) * sol_price

            # Update trade record
            trade.selling_price = received_usd / trade.quantity
            trade.total_received_amount = received_usd
            trade.sell_date = timezone.now()
            trade.status = "CLOSED"
            trade.save()

            return trade
        except Exception as e:
            logger.error(f"Sell order failed: {str(e)}")
            raise ExecutionError(f"Sell execution failed: {str(e)}")

    def _get_quote(self, input_mint: str, output_mint: str, amount: int) -> dict:
        """Get swap quote from Jupiter API"""
        try:
            params = {
                "inputMint": input_mint,
                "outputMint": output_mint,
                "amount": str(amount),
                "slippageBps": "50",  # 0.5% slippage
                "feeBps": "10",  # 0.1% platform fee
                "onlyDirectRoutes": "false"
            }
            response = requests.get(f"{self.jup_base}/quote", params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise ExecutionError(f"Quote failed: {str(e)}")

    def _execute_swap(self, quote: dict) -> str:
        """Execute swap transaction on-chain"""
        try:
            # Get swap transaction
            headers = {"Content-Type": "application/json"}
            payload = {
                "quoteResponse": quote,
                "userPublicKey": str(self.wallet.pubkey()),
                "wrapAndUnwrapSol": True
            }
            response = requests.post(
                f"{self.jup_base}/swap",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            tx_data = base64.b64decode(response.json()['swapTransaction'])

            # Sign and send transaction
            tx = Transaction.deserialize(tx_data)
            tx.sign(self.wallet)
            tx_sig = self.rpc_client.send_transaction(tx).value

            # Confirm transaction
            timeout = 30
            start_time = timezone.now()
            while (timezone.now() - start_time).seconds < timeout:
                result = self.rpc_client.get_confirmed_transaction(tx_sig)
                if result.value: return tx_sig
                time.sleep(1)
            raise ExecutionError("Transaction confirmation timed out")
        except requests.RequestException as e:
            raise ExecutionError(f"Swap transaction failed: {str(e)}")