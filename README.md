# pyIcarus - Ponto App

Uma aplicação multiplataforma para registro automático de ponto de trabalho, desenvolvida em Python.

## Sobre o Projeto

O pyIcarus é uma ferramenta que automatiza o processo de registro de ponto de trabalho. Ele oferece uma interface gráfica que funciona em diferentes sistemas operacionais (Windows e Linux) e se adapta ao ambiente disponível (GTK ou PyQt).

## Tecnologias Utilizadas

- **Linguagem**: Python 3.12+
- **Interfaces Gráficas**:
  - GTK 3 (para ambientes Linux/GNOME)
  - PyQt6 (para Windows e outros ambientes)
- **Segurança**: Criptografia de credenciais usando a biblioteca cryptography

## Requisitos

### Linux
- Python 3.12+
- PyGObject (para interface GTK)
- PyQt6 (alternativa para ambientes sem GTK)
- Bibliotecas: requests, cryptography

### Windows
- Python 3.12+
- PyQt6
- Bibliotecas: requests, cryptography

## Instalação

> **ℹ️ Nota ℹ️**: Se já tiver __python__ instalado, os requisitos serão instalados através do script de inicialização `run_icarus.sh` | `run_icarus.bat`, porém alguns requisitos podem não estar funcionando perfeitamente.

### Linux

```bash
# Instale as dependências do sistema (para GTK)
sudo apt-get update
sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 python3-pip

# OU instale PyQt6 (alternativa)
pip install PyQt6

# Instale as dependências Python
pip install -r requirements.txt  # Para GTK
# OU
pip install -r requirements_pyqt.txt  # Para PyQt

# Torne os scripts executáveis
chmod +x run_icarus.sh
```

### Windows

```batch
# Instale as dependências Python
pip install -r requirements_pyqt.txt

# Execute o script batch
run_icarus.bat
```

### MacOS

```bash
# Torne o script executável
chmod +x run_icarus.sh

# Execute o script
./run_icarus.sh
``` 

## Uso

O script de inicialização detectará automaticamente o ambiente disponível (GTK ou PyQt) e iniciará a versão apropriada do aplicativo:

```bash
# Linux
./run_icarus.sh

# Windows
run_icarus.bat
```

Na primeira execução, você precisará configurar seu nome de usuário e senha. Essas informações serão salvas de forma segura no diretório de configuração do usuário.

## Segurança das Credenciais

**IMPORTANTE**: As credenciais são armazenadas localmente no computador do usuário:

- Em Linux: `~/.config/ponto_app/`
- Em Windows: `%APPDATA%\ponto_app\`

A senha é armazenada de forma criptografada usando a biblioteca cryptography com derivação de chave PBKDF2. O arquivo de configuração tem permissões restritas para garantir que apenas o usuário proprietário possa acessá-lo.

## Automatização

### Linux

#### Criar um atalho na área de trabalho:

```bash
# Crie um arquivo .desktop
cat > ~/.local/share/applications/ponto_app.desktop << EOL
[Desktop Entry]
Name=Ponto App
Comment=Aplicativo para registro de ponto
Exec=/caminho/completo/para/run_icarus.sh
Icon=clock
Terminal=false
Type=Application
Categories=Utility;
EOL

# Atualize a base de dados de aplicações
update-desktop-database ~/.local/share/applications
```

#### Agendar execução automática:

```bash
# Adicionar ao crontab para executar nos horários de ponto (8h, 12h, 13h, 17h)
crontab -e

# Adicione as linhas:
0 8 * * 1-5 /caminho/completo/para/run_icarus.sh --auto
0 12 * * 1-5 /caminho/completo/para/run_icarus.sh --auto
0 13 * * 1-5 /caminho/completo/para/run_icarus.sh --auto
0 17 * * 1-5 /caminho/completo/para/run_icarus.sh --auto
```

### Windows

#### Criar um atalho na área de trabalho:
1. Clique com o botão direito na área de trabalho
2. Selecione "Novo" > "Atalho"
3. Navegue até o arquivo `run_icarus.bat` e selecione-o
4. Dê um nome ao atalho (ex: "Ponto App")

#### Agendar execução automática:
1. Abra o "Agendador de Tarefas" do Windows
2. Crie uma nova tarefa básica
3. Configure para executar nos horários desejados (ex: 8h, 12h, 13h, 17h)
4. Selecione o arquivo `run_icarus.bat` como programa a ser executado
5. Adicione o parâmetro `--auto` para registro automático

### MacOS

### Para criar um executavel 
```bash
pip3 install pyinstaller
pyinstaller --windowed --onefile ponto_app_pyqt.py
```


## Funcionalidades

- Interface gráfica moderna e intuitiva
- Detecção automática do ambiente (GTK ou PyQt)
- Exibição de data e hora em tempo real
- Armazenamento seguro de credenciais
- Confirmação antes de registrar o ponto
- Exibição de mensagens de status e feedback
- Suporte a modo automático (com flag `--auto`)
