# Ponto App

Uma aplicação GUI nativa para Ubuntu que permite registrar seu ponto de trabalho.

## Instalação

### 1. Instale as dependências necessárias

```bash
# Instale as dependências do sistema
sudo apt-get update
sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 python3-pip python3-venv openssl

# Crie um ambiente virtual (opcional, mas recomendado)
python3 -m venv venv
source venv/bin/activate

# Instale as dependências Python
pip install -r requirements.txt
```

### 2. Torne o script executável

```bash
chmod +x ponto_app.py
```

### 3. Instale o arquivo .desktop para integração com o sistema

```bash
# Copie o arquivo .desktop para o diretório de aplicações
mkdir -p ~/.local/share/applications
cp ponto_app.desktop ~/.local/share/applications/

# Atualize a base de dados de aplicações
update-desktop-database ~/.local/share/applications
```

## Uso

Você pode iniciar o aplicativo de duas maneiras:

1. Pelo menu de aplicações do Ubuntu, procurando por "Ponto App"
2. Diretamente pelo terminal:

```bash
./ponto_app.py
```

Na primeira execução, você precisará configurar seu nome de usuário e senha. Essas informações serão salvas de forma segura no diretório `~/.config/ponto_app/`.

## Funcionalidades

- Interface gráfica moderna e intuitiva
- Exibição de data e hora em tempo real
- Armazenamento seguro de credenciais
- Confirmação antes de registrar o ponto
- Exibição de mensagens de status e feedback

## Segurança

A senha é armazenada de forma criptografada usando OpenSSL com a mesma chave de criptografia do script bash original. O arquivo de configuração tem permissões restritas (0600) para garantir que apenas o usuário proprietário possa acessá-lo.
