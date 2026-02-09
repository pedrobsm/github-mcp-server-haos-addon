# 🔧 Correções Aplicadas - GitHub MCP Server Add-on

## Problema 1 - Build/Registry
```
ERROR: Can't install ghcr.io/amd64-addon-github-mcp-server:1.0.0
[400] Head "https://ghcr.io/v2/amd64-addon-github-mcp-server/manifests/1.0.0": name invalid
```

## Problema 2 - S6 Overlay
```
s6-overlay-suexec: fatal: can only run as pid 1
```

## ✅ Correções Aplicadas

### 1. Removida referência à imagem do registry (config.json)
**Antes:**
```json
"image": "ghcr.io/{arch}-addon-github-mcp-server",
```

**Depois:**
```json
// Linha removida - usar build local
```

**Motivo:** Para add-ons locais (não publicados), o Home Assistant deve fazer build usando o Dockerfile, não tentar baixar imagens do GitHub Container Registry.

### 2. Ativado Docker API (config.json)
**Antes:**
```json
"docker_api": false,
```

**Depois:**
```json
"docker_api": true,
```

**Motivo:** O add-on precisa de acesso ao Docker para executar containers do GitHub MCP Server.

### 3. Implementada estrutura s6-overlay (NOVA CORREÇÃO)

**Problema:** Script executado diretamente causava erro "s6-overlay-suexec: fatal: can only run as pid 1"

**Solução:** Implementada estrutura completa s6-overlay:

#### Criado: `rootfs/etc/services.d/github-mcp-server/run`
```bash
#!/usr/bin/execlineb -P
with-contenv
s6-setuidgid root
/app/run.sh
```

#### Criado: `rootfs/etc/services.d/github-mcp-server/finish`
```bash
#!/usr/bin/execlineb -S0
s6-svscanctl -t /var/run/s6/services
```

#### Criado: `rootfs/etc/cont-init.d/00-init.sh`
Script de inicialização que:
- Valida configuração
- Verifica token GitHub
- Baixa imagem Docker MCP se necessário

**Motivo:** As imagens base do Home Assistant usam s6-overlay como init system. Os add-ons devem usar a estrutura de serviços s6 em vez de CMD direto.

### 4. Instalado bashio no Dockerfile

**Adicionado:**
```dockerfile
# Install bashio
RUN curl -J -L -o /tmp/bashio.tar.gz \
    "https://github.com/hassio-addons/bashio/archive/v0.16.2.tar.gz" \
    && mkdir /tmp/bashio \
    && tar zxvf /tmp/bashio.tar.gz --strip 1 -C /tmp/bashio \
    && mv /tmp/bashio/lib /usr/lib/bashio \
    && ln -s /usr/lib/bashio/bashio /usr/bin/bashio \
    && rm -rf /tmp/bashio /tmp/bashio.tar.gz
```

**Motivo:** Bashio fornece funções úteis para ler configuração do add-on de forma padrão.

### 5. Reescrito run.sh para usar bashio
**Motivo:** Bashio fornece funções úteis para ler configuração do add-on de forma padrão.

### 5. Reescrito run.sh para usar bashio
**Agora:**
```bash
#!/usr/bin/with-contenv bashio
export GITHUB_PERSONAL_ACCESS_TOKEN=$(bashio::config 'github_token')
export GITHUB_TOOLSETS=$(bashio::config 'toolsets')
export MCP_PORT=$(bashio::config 'port')
export LOG_LEVEL=$(bashio::config 'log_level')
```

**Motivo:** Com bashio instalado e s6-overlay configurado, pode-se usar a forma padrão de add-ons HA. A validação é feita no cont-init.d, o run.sh apenas inicia o serviço.

### 6. Removido CMD do Dockerfile
**Novo:**
``Motivo:** Com bashio instalado e s6-overlay configurado, pode-se usar a forma padrão de add-ons HA. A validação é feita no cont-init.d, o run.sh apenas inicia o serviço.

### 6. Removido CMD do Dockerfile

**Antes:**
```dockerfile
CMD ["/app/run.sh"]
```

**Depois:**
```dockerfile
# (sem CMD - s6-overlay gerencia automaticamente)
```

**Motivo:** Com s6-overlay, o init system gerencia os serviços automaticamente. O CMD é desnecessário.

### 7. Adicionado tmpfs (config.json)
**Novo:**
```json
"tmpfs": "size=64m,uid=0,rw",
```

**Motivo:** Espaço temporário para processos do add-on.

## 📋 Ficheiros Modificados

1. ✅ `/addons/github-mcp-server/config.json`
2. ✅ `/addons/github-mcp-server/Dockerfile`
3. ✅ `/addons/github-mcp-server/run.sh`
4. ✅ `rootfs/etc/services.d/github-mcp-server/run` (NOVO)
5. ✅ `rootfs/etc/services.d/github-mcp-server/finish` (NOVO)
6. ✅ `rootfs/etc/cont-init.d/00-init.sh` (NOVO)

## 📁 Nova Estrutura

```
/addons/github-mcp-server/
├── config.json
├── Dockerfile
├── run.sh
├── mcp_bridge/
│   ├── app.py
│   ├── mcp_client.py
│   ├── models.py
│   └── requirements.txt
└── rootfs/                    ← NOVO
    └── etc/
        ├── cont-init.d/       ← Scripts de inicialização
        │   └── 00-init.sh
        └── services.d/        ← Serviços s6-overlay
            └── github-mcp-server/
                ├── run        ← Inicia o serviço
                └── finish     ← Cleanup ao parar
```

## 🔄 Fluxo de Inicialização (S6-Overlay)

1. **s6-overlay init** - Sistema PID 1
2. **cont-init.d/00-init.sh** - Valida configuração, baixa imagem Docker
3. **services.d/github-mcp-server/run** - Inicia /app/run.sh
4. **run.sh** - Lê configuração e inicia FastAPI
5. **FastAPI** - Servidor HTTP wrapper para MCP
## 🚀 Próximos Passos

### 1. Desinstalar versão antiga (se instalada)
No Home Assistant:
- Supervisor → Add-ons → GitHub MCP Server
- Clicar em "Uninstall" (se já instalado)

### 2. Atualizar add-on no HAOS
```bash
# Copiar versão corrigida
scp -r /addons/github-mcp-server root@homeassistant.local:/addons/

# OU se já está no HAOS, apenas recarregar:
# Supervisor → Add-on Store → ⋮ → Check for updates
```

### 3. Instalar novamente
1. Supervisor → Add-on Store
2. Scroll down para "Local add-ons"
3. Encontrar "GitHub MCP Server"
4. Clicar "Install"
5. **Aguardar build** (pode demorar 3-5 minutos na primeira vez)

### 4. Configurar
Na tab "Configuration":
```yaml
github_token: ghp_seu_token_aqui
toolsets: repos,issues,pull_requests,projects
port: 8080
log_level: info
```

### 5. Iniciar
1. Tab "Info"
2. Clicar "Start"
3. Verificar tab "Log" para mensagens de sucesso

## 🔍 Logs Esperados (Sucesso)

```
[INFO] Starting GitHub MCP Server...
[INFO] Configuration:
[INFO]   Toolsets: repos,issues,pull_requests,projects
[INFO]   Port: 8080
[INFO]   Log Level: info
[INFO]   Token: ghp_***a0b1
[INFO] Checking for GitHub MCP Server Docker image...
[INFO] Pulling GitHub MCP Server Docker image...
[INFO] Starting FastAPI HTTP wrapper on port 8080...
INFO:     Started server process [XX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080
```

## 🧪 Testar Instalação

### Via CLI do HAOS
```bash
# Health check
curl http://localhost:8080/health

# Esperado:
# {"status":"healthy","docker_accessible":true,"version":"1.0.0"}
```

### Via browser
- Abrir: http://homeassistant.local:8123/api/hassio_ingress/[SLUG]/docs
- Ou testar diretamente: http://homeassistant.local:8080/health

## ❓ Troubleshooting

### Se o build falhar
Verificar logs durante instalação para mensagens de erro específicas.

### Se "Docker not accessible"
Verificar que `docker_api: true` está no config.json.

### Se "GitHub token required"
Configurar token na tab Configuration do add-on.

### Se port 8080 já em uso
Mudar `port` na configuração para outro valor (ex: 8081).

## 📝 Notas Importantes

1. **Build Local**: Agora o add-on faz build local, não precisa do GitHub
2. **Docker Access**: O add-on agora tem permissão para usar Docker
3. **Configuração JSON**: Usa método padrão do Home Assistant (/data/options.json)
4. **Primeira instalação**: Pode demorar 3-5 minutos (download de dependências)

---

**Data:** 9 de Fevereiro de 2026  
**Versão:** 1.0.0 (corrigida)  
**Status:** ✅ Pronto para reinstalação
