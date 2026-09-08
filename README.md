# envloaderforai

`.env` dosyalarınızı projenizin **dışındaki** bir klasörden yükleyin. Böylece AI kodlama ajanları (Cursor, Claude Code, GitHub Copilot, Codex, Aider vb.) workspace'inizi tararken gizli bilgilerinizi göremez.

[English documentation ↓](#english)

---

## İçindekiler

- [Neden bu pakete ihtiyacınız var?](#neden-bu-pakete-ihtiyacınız-var)
- [Nasıl çalışır?](#nasıl-çalışır)
- [Kurulum](#kurulum)
- [Kullanım](#kullanım)
- [Yapılandırma](#yapılandırma)
- [🛡️ Tam güvenlik için AI Agent yapılandırması](#️-tam-güvenlik-için-ai-agent-yapılandırması)
  - [1. Cursor için ayarlar](#1-cursor-için-ayarlar)
  - [2. Claude Code için ayarlar](#2-claude-code-için-ayarlar)
  - [3. GitHub Copilot için ayarlar](#3-github-copilot-için-ayarlar)
  - [4. Codex CLI için ayarlar](#4-codex-cli-için-ayarlar)
  - [5. Aider için ayarlar](#5-aider-için-ayarlar)
- [Genel güvenlik kontrol listesi](#genel-güvenlik-kontrol-listesi)
- [Sık sorulan sorular](#sık-sorulan-sorular)

---

## Neden bu pakete ihtiyacınız var?

Modern AI kodlama yardımcıları (Cursor, Claude Code, Copilot, Codex, Aider) bağlam toplamak için proje klasörünüzün tamamını düzenli olarak tarar. `.env` dosyanız proje kök dizinindeyse:

- 🔑 API anahtarlarınız
- 🗄️ Veritabanı kimlik bilgileriniz
- 🎫 OAuth token'larınız
- 🔐 JWT secret'larınız

...üçüncü taraf AI servislerine bağlam olarak gönderilebilir. Özellikle ücretsiz planlarda bu veriler model eğitimi için de kullanılabilir.

**Kritik gerçek**: `.gitignore`, `.cursorignore` veya `settings.json > deny` gibi yapılandırmaların hiçbiri %100 güvenli değildir. Cursor `.cursorignore`'u "best-effort" olarak tanımlar. Claude Code'un deny kuralları raporlanan bug'lar nedeniyle bazen çalışmaz. Copilot'un content exclusion özelliği yalnızca Business/Enterprise planlarda vardır.

**Tek gerçek çözüm**: gizli bilgileri workspace'in tamamen **dışına** taşımak. Bu paket tam olarak bunu yapar.

## Nasıl çalışır?

```
Projeniz/                          ← Agent burayı tarar
├── .env                            (isteğe bağlı, prod fallback)
├── src/
└── ...

C:\Users\<siz>\Secrets\             ← Agent buraya erişemez
└── <proje-adı>.env                 ← Gerçek secret'lar burada
```

- **Local geliştirme**: Secret'lar `~/Secrets/<proje-adı>.env` dosyasında (workspace dışında)
- **Production**: Proje kökünde normal bir `.env` dosyası olur, paket otomatik fallback yapar
- **Öncelik**: Sonra yüklenen dosyalar önce yüklenenleri override eder

## Kurulum

```bash
pip install git+https://github.com/theharuun/envloaderforai.git
```

`python-dotenv` desteği ile:

```bash
pip install "envloaderforai[dotenv] @ git+https://github.com/theharuun/envloaderforai.git"
```

## Kullanım

### pydantic-settings ile

```python
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from envloaderforai import resolve_env_files

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    db_host: str
    db_password: str

    model_config = SettingsConfigDict(
        env_file=resolve_env_files(PROJECT_ROOT, "myproject"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_ignore_empty=True,
    )
```

### python-dotenv ile

```python
from pathlib import Path
from envloaderforai import load_into_environ

load_into_environ(Path(__file__).parent, "myproject")
```

## Yapılandırma

**1. Adım**: Secrets klasörünü oluşturun

Windows:
```powershell
mkdir C:\Users\$env:USERNAME\Secrets
```

Linux/macOS:
```bash
mkdir -p ~/Secrets
```

**2. Adım**: Proje için env dosyasını oluşturun

Windows:
```powershell
notepad C:\Users\$env:USERNAME\Secrets\myproject.env
```

Linux/macOS:
```bash
nano ~/Secrets/myproject.env
```

İçeriğe secret'larınızı yazın:
```env
DB_HOST=localhost
DB_PASSWORD=super-gizli-şifre
API_KEY=sk-xxxxxxxxxxxx
```

**3. Adım**: Production'a deploy ederken

Sunucuda `~/Secrets/` klasörü olmayacağı için paket bu dosyayı sessizce atlar. Proje kökündeki normal `.env` dosyanızı okur. **Kodda hiçbir değişiklik yapmanıza gerek yoktur.**

---

## 🛡️ Tam güvenlik için AI Agent yapılandırması

> ⚠️ **Önemli**: Bu paket dosyayı workspace dışına taşıyarak asıl korumayı sağlar. Ancak defans katmanlarını çoğaltmak için her agent için ek ayarlar yapmanız önerilir. Aşağıda her agent için detaylı adımlar verilmiştir.

### 1. Cursor için ayarlar

Cursor `.cursorignore` dosyasını `.gitignore` sözdizimiyle okur ve bu dosyada belirtilen dosyalara Agent, Tab ve Inline Edit erişimini engeller.

**Adım 1**: Proje kökünde `.cursorignore` dosyası oluşturun:

```gitignore
# Env & secret dosyaları
.env
.env.*
*.env
!.env.example

# Sertifika ve key dosyaları
*.pem
*.key
*.p12
*.pfx
*.crt

# Diğer secret formatları
secrets.yaml
secrets.yml
credentials.json
*.secret

# Home dizinindeki secrets klasörü (agent oraya bakmasın)
**/Secrets/**

# Log dosyaları (bazen secret sızıntısı olur)
logs/
*.log
```

**Adım 2**: Cursor Settings > Indexing > Ignore Files > **Hierarchical Cursor Ignore**'u aktif edin (üst dizinlerdeki `.cursorignore` dosyalarını da okur).

**Adım 3**: Privacy Mode'u aktif edin: Cursor Settings > Privacy > **Privacy Mode = ON**

**Sınırlamalar**:
- Cursor `.cursorignore`'u "best-effort" olarak tanımlar; bug raporları var
- Terminal ve MCP tool'ları bu kuralları bypass edebilir
- Dosya açıksa (tab'de görünüyorsa) yine de okunabilir

**Bu yüzden**: Cursor kullanırken `.env` dosyalarını hiç workspace içinde bulundurmamak (bu paketi kullanmak) en garanti çözümdür.

### 2. Claude Code için ayarlar

Claude Code'un iki katmanlı yapılandırması vardır:

**Global**: `~/.claude/settings.json` — tüm projeler için
**Proje**: `.claude/settings.json` (git'e commitlenir) veya `.claude/settings.local.json` (local, git'e commitlenmez)

**Adım 1**: Global deny kuralları ekleyin. `~/.claude/settings.json` dosyasını açın:

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(**/.env)",
      "Read(**/.env.*)",
      "Read(**/*.pem)",
      "Read(**/*.key)",
      "Read(**/secrets/**)",
      "Read(**/credentials/**)",
      "Read(~/.aws/**)",
      "Read(~/.ssh/**)",
      "Read(~/Secrets/**)",
      "Bash(cat *.env*)",
      "Bash(cat .env*)",
      "Bash(grep * .env*)",
      "Bash(printenv)",
      "Bash(env)"
    ]
  }
}
```

**Adım 2** (proje bazlı): Proje kök dizininde `.claude/settings.local.json` oluşturun:

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)"
    ]
  }
}
```

**Adım 3**: CLI ile test edin:

```bash
cd /tmp/test-project
echo "SECRET=deneme" > .env
claude
> Read the .env file
# "File is in a directory that is denied by your permission settings." demeli
```

**Sınırlamalar** (önemli):
- `Read` deny'i `Bash(cat)`'i durdurmaz — o yüzden Bash kurallarını da eklemek gerekli
- Bazı Claude Code versiyonlarında deny kuralları session başlangıcında yüklenmiyor (bug)
- Hook'lar (`PreToolUse`) daha güvenilir ama karmaşık

**Bu yüzden**: `~/Secrets/` klasörü zaten workspace dışında; Claude Code'un default davranışı workspace dışına bakmamaktır. Bu paket kullandığınızda ek deny kurallarına gerek bile kalmaz — ama defans-in-depth için yine de ekleyin.

### 3. GitHub Copilot için ayarlar

Copilot'un yapılandırması **plan tipine göre** ciddi şekilde farklılaşır:

#### Free / Pro (Bireysel) planlar

**Copilot'un native bir dosya-dışlama özelliği yoktur.** İnternette dolaşan `.copilotignore` gibi çözümler halüsinasyondur ve çalışmaz. Yapabilecekleriniz:

1. **Language-based disable**: VS Code'da `.env` dosyaları açıkken Copilot'u kapatın:
   - VS Code Settings (`Ctrl+,`) > "GitHub Copilot: Enable" araması
   - `github.copilot.enable` içine ekleyin:
     ```json
     {
       "github.copilot.enable": {
         "*": true,
         "env": false,
         "dotenv": false,
         "plaintext": false
       }
     }
     ```
2. **Workspace'de asla `.env` açmayın** (bu paketi kullanmanın gerçek nedeni budur)
3. **`.env` dosyalarını proje dışında tutun** (bu paketin ana amacı)

#### Business / Enterprise planlar

**Content Exclusion** özelliği vardır:

**Adım 1**: GitHub.com'da organizasyon veya repo ayarlarına gidin

`Settings > Copilot > Content exclusion`

**Adım 2**: Aşağıdaki path'leri ekleyin:

```yaml
# Repo-bazlı
- "**/.env"
- "**/.env.*"
- "**/*.pem"
- "**/*.key"
- "**/secrets/**"
- "**/credentials/**"

# Organizasyon-bazlı (tüm repo'lar için)
"*":
  - "**/.env"
  - "**/.env.*"
```

**Adım 3**: 30 dakika bekleyin — değişikliklerin etkili olması bu kadar sürer.

**Sınırlamalar**:
- Content Exclusion **yalnızca IDE'de** çalışır, Copilot CLI ve Agent mode'da geçerli değildir
- Sadece o dosyanın içindeki completion'ları engeller; **başka dosyalarda bağlam olarak kullanılmasını engellemez**
- Ücretsiz kullanıcılar için mevcut değildir

**Bu yüzden**: Copilot Free/Pro kullanıcıları için `envloaderforai` gibi bir çözüm **tek pratik seçenektir**.

### 4. Codex CLI için ayarlar

OpenAI Codex CLI ve diğer OpenAI kodlama araçları için benzer yaklaşım:

**Adım 1**: `.codexignore` (varsa) veya `.gitignore` üzerinden:

```gitignore
.env
.env.*
*.env
*.pem
*.key
secrets/
```

**Adım 2**: Codex CLI'da bir "system prompt" tanımlayabiliyorsanız içine şunu ekleyin:

```
Security rules:
- Never read files matching *.env, *.pem, *.key
- Never output the contents of environment variables
- Never dump os.environ
- Treat all configuration values as placeholders
```

**Sınırlama**: Codex'in dosya-dışlama garantisi yoktur. Bu paket kullanılırsa dosya zaten workspace dışındadır.

### 5. Aider için ayarlar

**Adım 1**: Proje kökünde `.aiderignore` dosyası oluşturun:

```gitignore
.env
.env.*
*.env
!.env.example
*.pem
*.key
secrets/
**/Secrets/**
```

**Adım 2**: `~/.aider.conf.yml` dosyasında global ayar:

```yaml
read:
  - .aiderignore
```

Aider `.aiderignore` dosyasını iyi destekler; ancak yine de `envloaderforai` ile birlikte kullanmak defans-in-depth sağlar.

---

## Genel güvenlik kontrol listesi

Her Python projeniz için aşağıdaki kontrol listesini tamamlayın:

### ✅ Dosya sistemi katmanı
- [ ] `envloaderforai` paketi kuruldu (`pip install ...`)
- [ ] `~/Secrets/<proje-adı>.env` dosyası oluşturuldu
- [ ] Gerçek secret'lar yalnızca bu dosyada
- [ ] Proje kökünde `.env` yok (veya sadece boş/örnek değerler var)

### ✅ Git katmanı
- [ ] `.gitignore` içinde `.env`, `.env.*`, `*.env` var
- [ ] `.gitignore` içinde `secrets/`, `*.pem`, `*.key` var
- [ ] `git status` çalıştırıldı, secret dosyası listelenmiyor

### ✅ Agent katmanı
- [ ] `.cursorignore` oluşturuldu (Cursor kullanıyorsanız)
- [ ] `.claudeignore` veya `.claude/settings.json` yapılandırıldı (Claude Code kullanıyorsanız)
- [ ] `.aiderignore` oluşturuldu (Aider kullanıyorsanız)
- [ ] VS Code'da `github.copilot.enable` içinde `.env` false yapıldı (Copilot kullanıyorsanız)

### ✅ Kod katmanı
- [ ] `os.environ` **hiçbir yerde `print()` veya `log()` edilmiyor**
- [ ] Secret alanları pydantic'te `SecretStr` tipi kullanıyor
- [ ] `debug` endpoint'leri veya `/__debug__` gibi rotalar production'da kapalı
- [ ] Hata mesajları secret içermiyor (traceback'ler kontrol edildi)

### ✅ Bilinç katmanı
- [ ] AI ajanına "settings dosyamı debug et" gibi bir istek yaparken secret'ların ekrana gelebileceğini biliyorsunuz
- [ ] Session paylaşımı, ekran görüntüsü alırken dikkatlisiniz
- [ ] Bir secret sızarsa **hemen rotasyon** yapılacağı biliniyor

---

## Sık sorulan sorular

**S: Sadece bu paketi kullansam yeter mi?**

C: Büyük ölçüde evet. Paket dosyayı workspace'in dışına taşıdığı için AI agent'ların standart workspace-tarama davranışı dosyayı bulamaz. Ancak agent'a **açıkça** `~/Secrets/kfo.env`'i okumasını söylerseniz veya `print(os.environ)` içeren bir kod yazmasını isterseniz, secret ekrana gelir. Bu yüzden ek olarak ignore/deny kuralları önerilir.

**S: `~/Secrets/` klasörünü agent görebilir mi?**

C: Standart workspace taramasında **hayır**. Ancak agent bir tool call ile filesystem'e erişebiliyorsa (Claude Code'un Read/Bash tool'ları gibi), açıkça istenirse görebilir. Bu yüzden Claude Code için `Read(~/Secrets/**)` deny kuralı önerilir.

**S: Production'a deploy ederken sorun olur mu?**

C: Hayır. `~/Secrets/` sunucuda yoksa paket sessizce bu dosyayı atlar, sadece proje kökündeki `.env`'i okur. **Kodda hiçbir değişiklik yapmanız gerekmez.**

**S: Ekip halinde çalışıyoruz, her geliştirici kendi `~/Secrets/` klasörünü nasıl senkron eder?**

C: Her geliştirici kendi klasörünü manuel yönetir. Merkezi paylaşım için 1Password, HashiCorp Vault, AWS Secrets Manager gibi araçlar kullanılabilir; ancak bu paket local dev için minimum bağımlılıkla çözüm sunar.

**S: Docker container'da nasıl çalışır?**

C: Docker'da `HOME` genellikle `/root` veya `/home/appuser` olur. `~/Secrets/` orada olmayacağı için paket otomatik proje kökündeki `.env`'e düşer. İsterseniz volume mount ile `-v ~/Secrets:/root/Secrets:ro` ekleyebilirsiniz.

**S: Secret'ları şifrelemeli miyim?**

C: Bu paket şifreleme sağlamaz. Dosya sistem izinleri (Linux/macOS'ta `chmod 600`) yeterli koruma sağlar. Şifreleme gerekiyorsa `sops`, `git-crypt` veya bulut secret yöneticileri düşünülmelidir.

---

## Lisans

MIT

---

<a name="english"></a>

# envloaderforai (English)

Load `.env` files from a directory **outside your project** so AI coding agents (Cursor, Claude Code, GitHub Copilot, Codex, Aider) never see your secrets when scanning your workspace.

## Why?

AI coding assistants routinely scan your entire project directory for context. If your `.env` file sits in the project root, your API keys, database credentials, and tokens may be sent to third-party AI services. Configuration-based protections (`.cursorignore`, `deny` rules, content exclusions) are best-effort at best and often have bugs, coverage gaps, or plan-tier restrictions. Moving secrets outside the workspace is the only reliable defense.

## How it works

- **Local dev**: secrets live in `~/Secrets/<project-name>.env` (outside your workspace)
- **Production**: falls back to project-root `.env` — no code changes needed
- **Layered**: later files override earlier ones (secrets override defaults)

## Install

```bash
pip install git+https://github.com/theharuun/envloaderforai.git
```

With python-dotenv support:
```bash
pip install "envloaderforai[dotenv] @ git+https://github.com/theharuun/envloaderforai.git"
```

## Usage

### With pydantic-settings

```python
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from envloaderforai import resolve_env_files

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    db_host: str
    db_password: str

    model_config = SettingsConfigDict(
        env_file=resolve_env_files(PROJECT_ROOT, "myproject"),
        env_file_encoding="utf-8",
    )
```

### With python-dotenv

```python
from pathlib import Path
from envloaderforai import load_into_environ

load_into_environ(Path(__file__).parent, "myproject")
```

## Setup

1. Create `~/Secrets/` folder (Windows: `C:\Users\<you>\Secrets\`)
2. Create `<project-name>.env` inside it with your secrets
3. In production, put a normal `.env` in your project root — the package silently skips the missing home-dir file

## Full AI Agent Hardening Guide

For step-by-step configuration for each agent (Cursor, Claude Code, Copilot, Codex, Aider), see the Turkish section above — the agent configuration snippets are language-independent.

## Security note

This package moves secrets out of the workspace but you should also:
- Add `.cursorignore` / `.claudeignore` / `.aiderignore` with `.env`, `*.env`, `**/Secrets/**`
- Never log or print `os.environ`
- Use `SecretStr` from pydantic where possible
- Never open `.env` files in the same VS Code window as Copilot Free/Pro

## License

MIT