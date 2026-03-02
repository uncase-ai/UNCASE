# Guia de Configuracion de Polygon para Blockchain

Guia completa para configurar la capa de certificacion blockchain de UNCASE con Polygon PoS. Esto permite verificacion de calidad inmutable y on-chain para cada dataset sintetico que produzcas.

---

## Tabla de Contenidos

1. [Panorama General](#1-panorama-general)
2. [Requisitos Previos](#2-requisitos-previos)
3. [Crear una Wallet con MetaMask](#3-crear-una-wallet-con-metamask)
4. [Agregar la Red Polygon](#4-agregar-la-red-polygon)
5. [Obtener Tokens POL (Gas)](#5-obtener-tokens-pol-gas)
6. [Desplegar el Contrato Inteligente](#6-desplegar-el-contrato-inteligente)
7. [Configurar el Entorno UNCASE](#7-configurar-el-entorno-uncase)
8. [Probar la Integracion](#8-probar-la-integracion)
9. [Ver Transacciones en PolygonScan](#9-ver-transacciones-en-polygonscan)
10. [Checklist de Produccion](#10-checklist-de-produccion)
11. [Solucion de Problemas](#11-solucion-de-problemas)
12. [Mejores Practicas de Seguridad](#12-mejores-practicas-de-seguridad)

---

## 1. Panorama General

### Que es Polygon PoS?

Polygon PoS (Proof of Stake) es una sidechain de Ethereum que ofrece transacciones rapidas y de bajo costo, heredando la seguridad de Ethereum. UNCASE usa Polygon para anclar raices de Merkle de reportes de evaluacion de calidad, creando un rastro de auditoria permanente e inalterable.

### Como usa UNCASE el Blockchain

```
Reporte de Evaluacion --> Hash SHA-256 --> Arbol de Merkle --> Anclar Raiz On-Chain
```

1. **Hash**: Cada reporte de evaluacion de calidad se serializa a JSON canonico y se hashea con SHA-256.
2. **Lote (Batch)**: Multiples hashes se agrupan en un arbol binario de Merkle.
3. **Anclar**: La raiz del Merkle se envia a un contrato inteligente en Polygon.
4. **Verificar**: Cualquier persona puede verificar independientemente un reporte recalculando su hash, recorriendo la prueba de Merkle y comparando la raiz con el registro on-chain.

### Por que Polygon?

| Caracteristica | Polygon PoS |
|----------------|-------------|
| Costo por transaccion | ~$0.001-0.01 USD |
| Tiempo de confirmacion | ~2 segundos |
| Seguridad | Hereda el conjunto de validadores de Ethereum |
| Explorador de bloques | PolygonScan (transparencia total) |
| Token | POL (anteriormente MATIC) |

---

## 2. Requisitos Previos

Antes de comenzar, asegurate de tener:

- Un navegador web (Chrome, Firefox o Brave recomendados)
- El backend de UNCASE corriendo (`uv run uvicorn uncase.api.main:app --reload`)
- Python 3.11+ con el extra `[blockchain]` instalado:
  ```bash
  pip install "uncase[blockchain]"
  # o con uv:
  uv sync --extra blockchain
  ```
- Node.js 18+ (para desplegar el contrato, si lo haces desde el codigo fuente)

---

## 3. Crear una Wallet con MetaMask

MetaMask es una extension de navegador que actua como tu wallet de Ethereum/Polygon.

### Paso 1: Instalar MetaMask

1. Ve a [metamask.io](https://metamask.io/download/)
2. Haz clic en **Download** para tu navegador
3. Haz clic en **Add to Chrome** (o tu navegador)
4. Fija la extension de MetaMask en tu barra de herramientas

### Paso 2: Crear una Wallet Nueva

1. Haz clic en el icono de MetaMask en tu barra de herramientas
2. Haz clic en **Create a new wallet**
3. Establece una contrasena segura (esta es tu contrasena de desbloqueo local)
4. **CRITICO**: Anota tu Frase de Recuperacion Secreta de 12 palabras en papel
   - Guardala en un lugar seguro y fuera de linea
   - Nunca la compartas con nadie
   - Nunca la almacenes digitalmente (ni capturas de pantalla, ni almacenamiento en la nube)
5. Confirma la frase de recuperacion seleccionando las palabras en orden
6. Tu wallet ya esta lista

### Paso 3: Exportar tu Clave Privada

UNCASE necesita la clave privada de la wallet que firmara las transacciones de anclaje.

1. Haz clic en los tres puntos (menu) junto al nombre de tu cuenta
2. Selecciona **Account details**
3. Haz clic en **Show private key**
4. Ingresa tu contrasena de MetaMask
5. Copia la clave privada (empieza con `0x`)
6. La usaras en el archivo `.env` (Paso 7)

> **IMPORTANTE**: La clave privada da control total sobre esta wallet. Para produccion, usa una wallet dedicada con fondos minimos (solo lo suficiente para gas). Nunca uses tu wallet personal.

---

## 4. Agregar la Red Polygon

### Testnet Amoy (Recomendado para Pruebas)

1. Abre MetaMask
2. Haz clic en el dropdown de redes (arriba a la izquierda, dice "Ethereum Mainnet")
3. Haz clic en **Add network** > **Add a network manually**
4. Ingresa:
   - **Network Name**: Polygon Amoy Testnet
   - **RPC URL**: `https://rpc-amoy.polygon.technology`
   - **Chain ID**: `80002`
   - **Currency Symbol**: `POL`
   - **Block Explorer**: `https://amoy.polygonscan.com`
5. Haz clic en **Save**

### Polygon Mainnet (Para Produccion)

1. Los mismos pasos que arriba, pero ingresa:
   - **Network Name**: Polygon Mainnet
   - **RPC URL**: `https://polygon-rpc.com`
   - **Chain ID**: `137`
   - **Currency Symbol**: `POL`
   - **Block Explorer**: `https://polygonscan.com`
2. Haz clic en **Save**

### Alternativa: Usar Chainlist

1. Ve a [chainlist.org](https://chainlist.org)
2. Busca "Polygon" o "Amoy"
3. Haz clic en **Add to MetaMask** en la red deseada

---

## 5. Obtener Tokens POL (Gas)

### Testnet (Amoy) - Faucet Gratis

Para pruebas, puedes obtener POL de testnet gratis:

1. Ve al [Polygon Faucet](https://faucet.polygon.technology/)
2. Selecciona la red **Amoy**
3. Pega tu direccion de wallet (copiala de MetaMask)
4. Completa la verificacion
5. Haz clic en **Submit**
6. Recibiras 0.5 POL en unos segundos

Faucets alternativos:
- [Alchemy Amoy Faucet](https://www.alchemy.com/faucets/polygon-amoy)
- [QuickNode Polygon Faucet](https://faucet.quicknode.com/polygon/amoy)

### Mainnet - Comprar POL

Para produccion, necesitas tokens POL reales:

**Opcion A: Comprar directamente en MetaMask**
1. Abre MetaMask en Polygon Mainnet
2. Haz clic en **Buy**
3. Elige un metodo de pago (tarjeta de credito, transferencia bancaria)
4. Compra tokens POL

**Opcion B: Comprar en un exchange y transferir**
1. Compra POL en un exchange (Coinbase, Binance, Kraken, etc.)
2. Retira a tu direccion de wallet de MetaMask
3. Asegurate de seleccionar la red **Polygon** para el retiro (no Ethereum)

**Opcion C: Bridge desde Ethereum**
1. Si tienes ETH, usa el [Polygon Bridge](https://portal.polygon.technology/bridge)
2. Conecta tu MetaMask
3. Pasa ETH a Polygon (se convierte en WETH en Polygon)
4. Intercambia WETH por POL en un DEX como [QuickSwap](https://quickswap.exchange)

> **Cuanto POL necesito?** Cada transaccion de anclaje cuesta aproximadamente 0.001-0.01 POL (~$0.001-0.01 USD). Para uso moderado (100 batches/mes), 1 POL es mas que suficiente.

---

## 6. Desplegar el Contrato Inteligente

UNCASE usa un contrato minimalista `UNCASEAuditAnchor`. Puedes desplegarlo usando Remix IDE o Hardhat.

### Codigo del Contrato Inteligente

Crea un archivo llamado `UNCASEAuditAnchor.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title UNCASEAuditAnchor
/// @notice Almacena raices de Merkle para lotes de evaluacion de calidad de UNCASE
contract UNCASEAuditAnchor {
    address public owner;

    struct AnchorRecord {
        bytes32 root;
        uint256 timestamp;
    }

    mapping(uint256 => AnchorRecord) public anchors;

    event RootAnchored(uint256 indexed batchId, bytes32 root, uint256 timestamp);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    /// @notice Ancla una raiz de Merkle para un lote
    /// @param batchId Identificador secuencial del lote
    /// @param root Raiz de Merkle SHA-256 (32 bytes)
    function anchorRoot(uint256 batchId, bytes32 root) external onlyOwner {
        require(anchors[batchId].timestamp == 0, "Batch already anchored");
        anchors[batchId] = AnchorRecord(root, block.timestamp);
        emit RootAnchored(batchId, root, block.timestamp);
    }

    /// @notice Verifica la raiz almacenada para un lote
    /// @param batchId El lote a consultar
    /// @return La raiz de Merkle almacenada (bytes32(0) si no se encuentra)
    function verifyRoot(uint256 batchId) external view returns (bytes32) {
        return anchors[batchId].root;
    }

    /// @notice Obtiene el timestamp de anclaje para un lote
    /// @param batchId El lote a consultar
    /// @return El timestamp del bloque cuando el lote fue anclado (0 si no se encuentra)
    function getTimestamp(uint256 batchId) external view returns (uint256) {
        return anchors[batchId].timestamp;
    }

    /// @notice Transferir propiedad
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "Zero address");
        owner = newOwner;
    }
}
```

### Desplegar con Remix IDE (Lo mas facil)

1. Ve a [Remix IDE](https://remix.ethereum.org)
2. Crea un nuevo archivo `UNCASEAuditAnchor.sol` y pega el codigo del contrato
3. Ve a la pestana **Solidity Compiler** (barra lateral izquierda)
   - Selecciona la version del compilador `0.8.20` o superior
   - Haz clic en **Compile**
4. Ve a la pestana **Deploy & Run**
   - Environment: **Injected Provider - MetaMask**
   - MetaMask te pedira conectarse - apruebalo
   - Asegurate de que MetaMask este en la red correcta (Amoy para pruebas)
5. Haz clic en **Deploy**
6. MetaMask mostrara una ventana pidiendo confirmar la transaccion
   - Revisa la tarifa de gas
   - Haz clic en **Confirm**
7. Espera el despliegue (~2 segundos en Polygon)
8. Copia la direccion del contrato desplegado (se muestra en "Deployed Contracts")
9. Usaras esta direccion en el archivo `.env` (Paso 7)

### Desplegar con Hardhat (Avanzado)

```bash
# Inicializar proyecto
mkdir uncase-contract && cd uncase-contract
npm init -y
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox

# Inicializar Hardhat
npx hardhat init
# Selecciona "Create a TypeScript project"

# Copia el contrato a contracts/UNCASEAuditAnchor.sol

# Crea el script de deploy (scripts/deploy.ts):
cat > scripts/deploy.ts << 'SCRIPT'
import { ethers } from "hardhat";

async function main() {
  const Contract = await ethers.getContractFactory("UNCASEAuditAnchor");
  const contract = await Contract.deploy();
  await contract.waitForDeployment();
  console.log("UNCASEAuditAnchor deployed to:", await contract.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
SCRIPT

# Configura hardhat.config.ts con la red Polygon
# Agrega a la seccion networks:
# amoy: {
#   url: "https://rpc-amoy.polygon.technology",
#   accounts: [process.env.PRIVATE_KEY]
# }

# Desplegar
npx hardhat run scripts/deploy.ts --network amoy
```

---

## 7. Configurar el Entorno UNCASE

Agrega las siguientes variables a tu archivo `.env` en la raiz del proyecto UNCASE:

```env
# --- Configuracion Blockchain ---
BLOCKCHAIN_ENABLED=true

# URL del RPC de Polygon
# Testnet (Amoy):
POLYGON_RPC_URL=https://rpc-amoy.polygon.technology
# Mainnet:
# POLYGON_RPC_URL=https://polygon-rpc.com

# Clave privada de la wallet que firma las transacciones
# IMPORTANTE: Usa una wallet dedicada, nunca la personal
POLYGON_PRIVATE_KEY=0xTU_CLAVE_PRIVADA_AQUI

# Direccion del contrato UNCASEAuditAnchor desplegado
POLYGON_CONTRACT_ADDRESS=0xTU_DIRECCION_DE_CONTRATO_AQUI

# Chain ID (80002 = Amoy testnet, 137 = Mainnet)
POLYGON_CHAIN_ID=80002
```

### Usar un Proveedor de RPC Premium (Recomendado para Produccion)

Los RPCs publicos gratuitos pueden ser lentos o tener limite de solicitudes. Para produccion, usa un proveedor dedicado:

| Proveedor | Tier Gratis | Formato de URL |
|-----------|-------------|----------------|
| [Alchemy](https://www.alchemy.com/) | 300M unidades de computo/mes | `https://polygon-amoy.g.alchemy.com/v2/TU_KEY` |
| [Infura](https://www.infura.io/) | 100K solicitudes/dia | `https://polygon-amoy.infura.io/v3/TU_KEY` |
| [QuickNode](https://www.quicknode.com/) | 10M creditos API/mes | URL de endpoint personalizado |
| [Ankr](https://www.ankr.com/) | Tier gratis con limite | `https://rpc.ankr.com/polygon_amoy` |

Ejemplo con Alchemy:
```env
POLYGON_RPC_URL=https://polygon-amoy.g.alchemy.com/v2/abc123tukey
```

---

## 8. Probar la Integracion

### Verificar Configuracion

Inicia la API de UNCASE y verifica las configuraciones de blockchain:

```bash
# Iniciar la API
uv run uvicorn uncase.api.main:app --reload --port 8000

# Verificar estadisticas de blockchain (deberia retornar ceros)
curl http://localhost:8000/api/v1/blockchain/stats
```

Respuesta esperada:
```json
{
  "total_hashed": 0,
  "total_batched": 0,
  "total_unbatched": 0,
  "total_batches": 0,
  "total_anchored": 0,
  "total_pending_anchor": 0,
  "total_failed_anchor": 0
}
```

### Ejecutar una Evaluacion y Verificar

1. Ejecuta una evaluacion de calidad a traves del pipeline (o via el dashboard)
2. El reporte de evaluacion se hasheara automaticamente
3. Ve a **Dashboard > Blockchain** y haz clic en **Build Batch**
4. El batch se creara y anclara en Polygon
5. Usa la pestana **Verify** para buscar el ID del reporte de evaluacion

### Prueba Manual con curl

```bash
# Construir un batch de hashes sin agrupar
curl -X POST http://localhost:8000/api/v1/blockchain/batch \
  -H "Content-Type: application/json" \
  -d '{}'

# Verificar una evaluacion especifica
curl http://localhost:8000/api/v1/blockchain/verify/{evaluation_report_id}

# Listar todos los batches
curl "http://localhost:8000/api/v1/blockchain/batches?limit=10"
```

---

## 9. Ver Transacciones en PolygonScan

### Encontrar tus Transacciones

**Via el Dashboard de UNCASE:**
1. Ve a **Dashboard > Blockchain**
2. En la pestana **Batch Ledger**, haz clic en cualquier hash de transaccion
3. Esto abre PolygonScan directamente

**Via PolygonScan:**
1. Ve a [amoy.polygonscan.com](https://amoy.polygonscan.com) (testnet) o [polygonscan.com](https://polygonscan.com) (mainnet)
2. Pega tu direccion de wallet o hash de transaccion en la barra de busqueda

### Entender la Transaccion

Cuando veas una transaccion en PolygonScan, encontraras:

- **Status**: Success / Failed
- **Block**: El numero de bloque donde se incluyo la transaccion
- **Timestamp**: Cuando se mino el bloque
- **From**: Tu direccion de wallet (el firmante)
- **To**: La direccion del contrato UNCASEAuditAnchor
- **Value**: 0 POL (es una transaccion de datos, no una transferencia)
- **Transaction Fee**: El costo de gas en POL
- **Input Data**: La llamada codificada `anchorRoot(batchId, root)`

### Leer el Log de Eventos

Haz clic en la pestana **Logs** en la pagina de la transaccion para ver:

```
Event: RootAnchored(uint256 batchId, bytes32 root, uint256 timestamp)
- batchId: 1 (el numero de batch)
- root: 0x7a8b... (el hash de la raiz de Merkle)
- timestamp: 1709312400 (timestamp Unix)
```

### Monitorear tu Contrato

1. Ve a la direccion de tu contrato en PolygonScan
2. Haz clic en la pestana **Events** para ver todos los eventos de anclaje
3. Haz clic en **Read Contract** para consultar `verifyRoot(batchId)` directamente
4. Haz clic en **Internal Txns** para ver todas las interacciones

### Configurar Alertas (Opcional)

PolygonScan ofrece alertas por email:
1. Crea una cuenta en PolygonScan
2. Ve a la pagina de tu contrato
3. Haz clic en **Watch** (icono del ojo)
4. Configura alertas por email para nuevas transacciones

---

## 10. Checklist de Produccion

Antes de ir a produccion, verifica:

- [ ] Cambiar de Amoy testnet a Polygon Mainnet (`POLYGON_CHAIN_ID=137`)
- [ ] Usar un proveedor de RPC premium (Alchemy, Infura, etc.)
- [ ] Desplegar el contrato en Mainnet
- [ ] Fondear la wallet con suficiente POL (~1 POL para meses de uso)
- [ ] Usar una wallet dedicada (no la personal)
- [ ] Almacenar la clave privada de forma segura (usar un gestor de secretos, no `.env` en texto plano)
- [ ] Verificar el contrato en PolygonScan (para verificacion publica)
- [ ] Configurar alertas de monitoreo en PolygonScan
- [ ] Probar el flujo completo: evaluar > hashear > batch > anclar > verificar
- [ ] Hacer respaldo de la frase de recuperacion de la wallet de forma segura

---

## 11. Solucion de Problemas

### "web3 is required for blockchain anchoring"

Instala las dependencias de blockchain:
```bash
pip install "uncase[blockchain]"
```

### "Failed to anchor root on-chain"

Causas comunes:
- **Fondos insuficientes**: Verifica el saldo de tu wallet en PolygonScan
- **Red incorrecta**: Verifica que `POLYGON_CHAIN_ID` coincida con la red de tu wallet
- **Problema de RPC**: Intenta con una URL de RPC o proveedor diferente
- **Desajuste de nonce**: Si las transacciones estan atoradas, revisa las transacciones pendientes en MetaMask

### "Batch already anchored"

El mismo ID de batch solo puede ser anclado una vez. Esto es por diseno - previene manipulacion. Si necesitas re-anclar, se debe crear un nuevo batch.

### La transaccion esta atorada / pendiente

1. Revisa la transaccion en PolygonScan
2. Si muestra "Pending", el precio del gas puede ser muy bajo
3. En MetaMask, puedes acelerar o cancelar la transaccion
4. Para la API de UNCASE, reintenta con `POST /api/v1/blockchain/retry-anchor`

### "Network error" o timeout de conexion

1. Verifica que la URL del RPC sea correcta y accesible
2. Intenta hacer ping al RPC: `curl https://rpc-amoy.polygon.technology -X POST -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'`
3. Cambia a un proveedor de RPC diferente

---

## 12. Mejores Practicas de Seguridad

### Seguridad de la Wallet

- **Usa una wallet dedicada** exclusivamente para el anclaje de UNCASE
- **Fondos minimos**: Solo ten suficiente POL para gas (~1 POL)
- **Respaldo**: Almacena la frase de recuperacion fuera de linea en un lugar seguro
- **Hardware wallet**: Para despliegues de alto valor, usa un Ledger o Trezor

### Gestion de Clave Privada

- **Nunca commits** la clave privada al control de versiones
- **Usa variables de entorno** o un gestor de secretos (AWS Secrets Manager, HashiCorp Vault)
- **Rota las claves** periodicamente transfiriendo la propiedad del contrato
- **Restringe el acceso**: Solo el servidor de despliegue debe tener la clave privada

### Seguridad del Contrato

- **Verifica en PolygonScan**: Publica el codigo fuente del contrato para transparencia
- **Solo el dueno puede escribir**: El contrato restringe `anchorRoot` a la direccion del dueno
- **Registros inmutables**: Una vez anclados, los registros no pueden ser modificados ni eliminados
- **Transferir propiedad**: Usa `transferOwnership()` si la wallet firmante necesita cambiar

### Monitoreo

- Configura alertas de email en PolygonScan para tu contrato
- Monitorea el saldo de la wallet para asegurar fondos suficientes para gas
- Revisa el dashboard de UNCASE para intentos fallidos de anclaje
- Revisa los logs de la API para eventos `anchor_root_failed`

---

## Referencia Rapida

| Elemento | Valor |
|----------|-------|
| Chain ID de Polygon Mainnet | `137` |
| Chain ID de Polygon Amoy Testnet | `80002` |
| RPC de Mainnet | `https://polygon-rpc.com` |
| RPC de Amoy | `https://rpc-amoy.polygon.technology` |
| Explorador de Mainnet | [polygonscan.com](https://polygonscan.com) |
| Explorador de Amoy | [amoy.polygonscan.com](https://amoy.polygonscan.com) |
| Token | POL (anteriormente MATIC) |
| Costo Promedio de Transaccion | ~$0.001-0.01 USD |
| Tiempo de Confirmacion | ~2 segundos |
| Endpoint Blockchain de UNCASE | `GET /api/v1/blockchain/stats` |
| Endpoint de Verificacion de UNCASE | `GET /api/v1/blockchain/verify/{id}` |
