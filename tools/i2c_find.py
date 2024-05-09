import smbus

def test_address(address):
    try:
        bus = smbus.SMBus(1)
        bus.write_byte(address, 0)  # Essayer d'écrire 0 à l'adresse
        print(f"Communication réussie à l'adresse {hex(address)}")
        return True
    except Exception as e:
        print(f"Erreur à l'adresse {hex(address)} : {str(e)}")
        return False

# Essayer différentes adresses
addresses_to_try = [0x27, 0x3F, 0x28, 0x29]

for address in addresses_to_try:
    test_address(address)
        
