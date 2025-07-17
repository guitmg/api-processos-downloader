FROM python:3.10-slim

WORKDIR /app
COPY . .

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    curl unzip gnupg libnss3 libxss1 libasound2 libatk-bridge2.0-0 libgtk-3-0 libgbm1 libx11-xcb1 libdrm2 libxcomposite1 libxrandr2 libxdamage1 libxext6 libxfixes3 fonts-liberation \
    && apt-get clean

# Instala Google Chrome
RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable

# Instala ChromeDriver compatível
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+') && \
    wget -O /tmp/chromedriver.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROME_VERSION/linux64/chromedriver-linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver

# Instala libs Python
RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 10000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]
