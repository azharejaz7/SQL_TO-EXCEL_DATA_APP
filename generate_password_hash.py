import bcrypt
import base64

def hash_password(password):
    """Hash a password for storing."""
    # Hash a password for the first time
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode()

# Generate hashed passwords for your users
password1 = "az4176"  # Replace with your actual password
password2 = "sal4176"  # Replace with your actual password

# Hash the passwords
hashed_password1 = hash_password(password1)
hashed_password2 = hash_password(password2)

print(f"Hashed password 1: {hashed_password1}")
print(f"Hashed password 2: {hashed_password2}")
print("\nAdd these to your .env file as:")
print(f"USER1_PASSWORD={hashed_password1}")
print(f"USER2_PASSWORD={hashed_password2}") 