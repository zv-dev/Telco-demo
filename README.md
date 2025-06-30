# Telco Microservices Demo

Ez a projekt egy modern, microservice-alapú architektúra bemutatója, amely különböző gyártók eszközeiből származó adatokat dolgoz fel, normalizál, és REST API-n keresztül elérhetővé tesz harmadik fél számára.

## Fő komponensek
- **input-vendor1, input-vendor2**: Szimulált adatokat generálnak és RabbitMQ-ra küldik.
- **processor**: Fogadja az üzeneteket, normalizálja, és adatbázisba menti.
- **api-gateway**: REST API-t biztosít a normalizált adatok lekérdezésére.
- **RabbitMQ**: Üzenetsor a service-ek között.
- **PostgreSQL**: Normalizált adatok tárolása.

## Infrastruktúra részletes leírása

### Áttekintés
A rendszer Docker Compose segítségével indítható, minden komponens külön konténerben fut. A komponensek egy közös Docker hálózaton kommunikálnak, így a service-ek hostnév alapján (pl. `rabbitmq`, `postgres`) érik el egymást.

### Komponensek és kapcsolatok
- **input-vendor1, input-vendor2**: Ezek a microservice-ek szimulált adatokat generálnak, és a RabbitMQ üzenetsorába (queue) küldik azokat. A RabbitMQ hostját a `RABBITMQ_HOST` környezeti változóval érik el (alapértelmezett: `rabbitmq`).
- **RabbitMQ**: Egy üzenetközvetítő (message broker), amely lehetővé teszi a laza csatolású, aszinkron kommunikációt a service-ek között. A producer service-ek (input-vendor1/2) üzeneteket küldenek a `raw_data` queue-ra, a processor service pedig consumerként olvassa ezeket.
- **processor**: Folyamatosan figyeli a RabbitMQ-t, feldolgozza az üzeneteket, normalizálja az adatokat, és eltárolja azokat a PostgreSQL adatbázisban.
- **PostgreSQL**: A normalizált adatok tartós tárolására szolgál.
- **api-gateway**: REST API-t biztosít, amelyen keresztül a normalizált adatok lekérdezhetők.

### RabbitMQ működése a rendszerben
- **Feladata**: Az adatok áramlásának központi eleme, amely lehetővé teszi, hogy a különböző gyártók adatai aszinkron módon, megbízhatóan jussanak el a feldolgozó service-hez.
- **Queue**: A rendszerben egy `raw_data` nevű queue-t használunk. Az input-vendor service-ek ide küldik az üzeneteket, a processor innen olvassa ki azokat.
- **Elérhetőség**:
  - **AMQP port**: 5672 (service-ek számára)
  - **Management UI**: 15672 ([http://localhost:15672](http://localhost:15672))
    - Felhasználónév: `user`
    - Jelszó: `password`
- **Hálózat**: A Docker Compose hálózatán keresztül a service-ek a `rabbitmq` hostnéven érik el a RabbitMQ-t.
- **Hibatűrés**: Ha a RabbitMQ nem elérhető, a producer vagy consumer service-ek hibát jeleznek, de újraindítás után automatikusan újra próbálkoznak.

### Példa adatfolyam
1. input-vendor1/2 → RabbitMQ (`raw_data` queue)
2. processor (consumer) → PostgreSQL (`normalized_data` tábla)
3. api-gateway → REST API (`/data` végpont)

## Projekt struktúra
```
telco/
├── docker-compose.yml
├── input-vendor1/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── input-vendor2/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── processor/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
└── api-gateway/
    ├── Dockerfile
    ├── main.py
    └── requirements.txt
```

## Rendszer indítása
1. Győződj meg róla, hogy a Docker és Docker Compose telepítve van.
2. A projekt gyökérkönyvtárában futtasd:

```bash
docker-compose up --build
```

Ez elindítja az összes service-t.

## Tesztelés menete

### 1. Service-ek ellenőrzése
- **RabbitMQ UI:**  [http://localhost:15672](http://localhost:15672)  
  Felhasználónév: `user`  
  Jelszó: `password`

- **API-gateway health check:**  
  [http://localhost:8000/health](http://localhost:8000/health)  
  Válasz:  `{ "status": "ok" }`

### 2. Adatok lekérdezése
- **Összes normalizált adat lekérdezése:**

  Böngészőben vagy terminálban:
  ```bash
  curl http://localhost:8000/data
  ```
  Válasz példa:
  ```json
  [
    {
      "id": 1,
      "vendor": "vendor1",
      "device_id": "dev-1234",
      "timestamp": 1710000000,
      "signal_strength": -80,
      "status": "active"
    },
    {
      "id": 2,
      "vendor": "vendor2",
      "device_id": "v2-54321",
      "timestamp": 1710000007,
      "signal_strength": -60,
      "status": "inactive"
    }
  ]
  ```

### 3. Logok ellenőrzése
- Minden service logja megjelenik a terminálban, ahol a `docker-compose up` fut.
- Egy adott service logjának megtekintése:
  ```bash
  docker-compose logs processor
  docker-compose logs input-vendor1
  docker-compose logs api-gateway
  ```

### 4. Adatbázis ellenőrzése
- Belépés a PostgreSQL konténerbe:
  ```bash
  docker-compose exec postgres psql -U telco -d telco_db
  ```
- Adatok lekérdezése SQL-ből:
  ```sql
  SELECT * FROM normalized_data;
  ```

## Hasznos linkek
- **Swagger/OpenAPI dokumentáció:** [http://localhost:8000/docs](http://localhost:8000/docs)

## Hibakeresés
- Ha valamelyik service nem indul, ellenőrizd a logokat.
- Ha a processor vagy az input-vendor service-ek nem tudnak csatlakozni a RabbitMQ-hoz, várj pár másodpercet, majd indítsd újra őket.
- Ha módosítasz egy service kódján, futtasd újra a build-et:
  ```bash
  docker-compose up --build
  ```

## Bővítés
- Új gyártóhoz új input service vagy a processor bővítése.
- API-gateway-hez szűrés, pagináció, jogosultságok egyszerűen hozzáadhatók.

---
