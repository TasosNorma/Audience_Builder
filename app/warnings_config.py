import warnings
from urllib3.exceptions import NotOpenSSLWarning

# Suppress specific urllib3 warning about OpenSSL
warnings.filterwarnings('ignore', category=NotOpenSSLWarning)