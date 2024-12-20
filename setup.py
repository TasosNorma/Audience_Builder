# from setuptools import setup, find_packages

# setup(
#     name="Audience_builder",
#     packages=find_packages()
# )

from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())  # This will print a string you can copy