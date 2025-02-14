from solders.keypair import Keypair
import base58

# Generate a new keypair
keypair = Keypair()

# Get private and public key
private_key = base58.b58encode(keypair.to_bytes()).decode("utf-8")
public_key = str(keypair.pubkey())

print("Solana Private Key:", private_key)
print("Solana Public Address:", public_key)
