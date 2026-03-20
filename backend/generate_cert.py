import datetime
import ipaddress
import sys
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_self_signed_cert(hostname_or_ip):
    print(f"Generating self-signed SSL certificate for {hostname_or_ip}...")
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Setup subject and issuer
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"TX"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Dallas"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"MAHER AI"),
        x509.NameAttribute(NameOID.COMMON_NAME, hostname_or_ip),
    ])

    cert_builder = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        # Valid for 10 years
        datetime.datetime.utcnow() + datetime.timedelta(days=3650) 
    )

    # Add Subject Alternate Name depending on if it's an IP or Hostname
    # Modern browsers require SANs
    try:
        ip = ipaddress.ip_address(hostname_or_ip)
        sans = [x509.IPAddress(ip)]
    except ValueError:
        sans = [x509.DNSName(hostname_or_ip)]
    
    sans.append(x509.DNSName("localhost"))
    sans.append(x509.IPAddress(ipaddress.ip_address("127.0.0.1")))

    cert_builder = cert_builder.add_extension(
        x509.SubjectAlternativeName(sans),
        critical=False,
    )

    cert = cert_builder.sign(private_key, hashes.SHA256())

    # Write private key
    with open("server.key", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
        
    # Write certificate
    with open("server.crt", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
        
    print(f"Successfully generated server.crt and server.key for {hostname_or_ip}")

if __name__ == "__main__":
    host = "127.0.0.1"
    if len(sys.argv) > 1:
        host = sys.argv[1]
    
    generate_self_signed_cert(host)
