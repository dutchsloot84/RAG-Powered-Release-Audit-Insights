FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 1) Add CA bundle + trust it system-wide, then install the build deps you already had
#    (ca-certificates is the key addition; update-ca-certificates merges your PEM)
COPY csaa_netskope_combined.pem /usr/local/share/ca-certificates/corp.crt
RUN chmod 644 /usr/local/share/ca-certificates/corp.crt \
    && apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates build-essential libgomp1 \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2) Now pip can reach PyPI through Netskope because the CA is trusted
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 3) Your app code
COPY . .

ENV PYTHONPATH=/app
# Optional "belt & suspenders" envs (some tools read these explicitly)
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
    SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt \
    PIP_CERT=/etc/ssl/certs/ca-certificates.crt

CMD ["streamlit", "run", "app/ui/ui_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
