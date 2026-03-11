const express = require('express');
const mysql = require('mysql2/promise');
const cors = require('cors');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname)));

const rand = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;
const randFloat = (min, max) => parseFloat((Math.random() * (max - min) + min).toFixed(2));
const randItem = arr => arr[Math.floor(Math.random() * arr.length)];

function randomDate(start, end) {
  const d = new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
  return d.toISOString().split('T')[0];
}

function addDays(dateStr, days) {
  const d = new Date(dateStr);
  d.setDate(d.getDate() + days);
  return d.toISOString().split('T')[0];
}

const now = new Date();
const twoYearsAgo = new Date(now); twoYearsAgo.setFullYear(now.getFullYear() - 2);
const threeYearsAgo = new Date(now); threeYearsAgo.setFullYear(now.getFullYear() - 3);
const oneYearAgo = new Date(now); oneYearAgo.setFullYear(now.getFullYear() - 1);
const sixMonthsAgo = new Date(now); sixMonthsAgo.setMonth(now.getMonth() - 6);

const countries = ["USA","China","Germany","India","Brazil","UK","Japan"];
const categories = ["Electronics","Packaging","Raw Materials","Machinery","Chemicals"];
const warehouses = ["Warehouse A","Warehouse B","Warehouse C","Warehouse D"];
const statuses = ["Pending","Delivered","Cancelled","In Transit"];
const shipStatuses = ["On Time","Delayed","Early"];
const carriers = ["FedEx","DHL","UPS","Maersk","DB Schenker"];

const companyNames = ["Nexus Supplies","Apex Logistics","CoreTech","BlueLine Co","SwiftParts",
  "TradeBridge","PrimeCargo","GlobalMesh","IronLink","SkyRoute","FlowChain","OmniSource",
  "PeakSupply","NorthStar Trading","ClearPath","RedRock Industries","Crestwood Supply",
  "Titan Freight","Vantage Corp","EchoMaterials","BrightEdge","FusionLogix","CarbonPath",
  "AlphaGoods","ZenithProcure","MidWest Freight","Coastline Parts","StellarTrade","IronWave",
  "CopperBay","NorthPeak","DeltaSupply","GoldMine Corp","SilverStream","BronzeWorks",
  "TitaniumHub","SteelRoute","AlloyCo","MetalBridge","WireLink","CircuitSource","DataParts",
  "ChipTrack","VoltageCo","AmpSupply","CurrentTrade","WaveFreight","PulseLogix","SignalPath","GridSource"];

const productNames = ["Steel Rod 10mm","Copper Wire 2kg","Circuit Board A3","Hydraulic Pump X2",
  "Packaging Film 50m","Industrial Solvent 5L","Gear Assembly V4","LED Module 24V",
  "Carbon Filter XL","Rubber Seal Pack","Aluminum Sheet 3mm","Titanium Bolt Set",
  "Plastic Casing B2","Power Cable 10m","Sensor Module T1","Valve Assembly K3",
  "Bearing Set 6200","Drive Belt 2m","Compressor Unit C5","Filter Cartridge F7",
  "Motor Winding M2","Control Panel CP1","Heat Sink H4","Fan Unit 12V","Battery Pack 48V",
  "Transformer T3","Relay Switch R2","Fuse Box FB1","Junction Box J5","Cable Tray CT2",
  "Pipe Fitting PF3","Flange Set FL2","Gasket Pack GP1","O-Ring Set OR4","Seal Kit SK2",
  "Bearing Housing BH1","Shaft Coupling SC3","Sprocket SP2","Chain Drive CD4","Pulley Set PL1",
  "Conveyor Belt CB2","Roller Assembly RA3","Guide Rail GR1","Linear Actuator LA2",
  "Pneumatic Cylinder PC3","Solenoid Valve SV1","Flow Meter FM2","Pressure Gauge PG3",
  "Temperature Sensor TS4","Level Indicator LI2"];

async function generateAll(io) {
  const conn = await mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'yourpassword',   // ← change this
    database: 'supply_chain',
    multipleStatements: true
  });

  const log = (msg, type = 'info') => io(msg, type);

  try {
    log('🔌 Connected to MySQL database...');
    await conn.execute('SET FOREIGN_KEY_CHECKS = 0');
    await conn.execute('TRUNCATE TABLE shipments');
    await conn.execute('TRUNCATE TABLE orders');
    await conn.execute('TRUNCATE TABLE inventory');
    await conn.execute('TRUNCATE TABLE products');
    await conn.execute('TRUNCATE TABLE suppliers');
    await conn.execute('SET FOREIGN_KEY_CHECKS = 1');
    log('🧹 Cleared existing data');

    log('⏳ Generating suppliers...');
    for (let i = 0; i < 50; i++) {
      await conn.execute(
        `INSERT INTO suppliers (supplier_name, country, contact_email, rating, lead_time_days, created_at) VALUES (?, ?, ?, ?, ?, ?)`,
        [companyNames[i], randItem(countries), `contact@${companyNames[i].toLowerCase().replace(/\s/g,'')}.com`,
         randFloat(2.5, 5.0), rand(3, 30), randomDate(threeYearsAgo, oneYearAgo)]
      );
    }
    log('✅ 50 Suppliers inserted', 'success');

    log('⏳ Generating products...');
    for (let i = 0; i < 200; i++) {
      await conn.execute(
        `INSERT INTO products (product_name, category, unit_price, reorder_level, supplier_id) VALUES (?, ?, ?, ?, ?)`,
        [productNames[i % productNames.length] + ` v${i+1}`, randItem(categories),
         randFloat(5, 500), rand(10, 100), rand(1, 50)]
      );
    }
    log('✅ 200 Products inserted', 'success');

    log('⏳ Generating inventory...');
    for (let i = 1; i <= 200; i++) {
      await conn.execute(
        `INSERT INTO inventory (product_id, warehouse_location, quantity_in_stock, last_updated) VALUES (?, ?, ?, ?)`,
        [i, randItem(warehouses), rand(0, 500), randomDate(sixMonthsAgo, now)]
      );
    }
    log('✅ 200 Inventory records inserted', 'success');

    log('⏳ Generating 5000 orders (this may take a moment)...');
    for (let i = 0; i < 5000; i++) {
      const orderDate = randomDate(twoYearsAgo, now);
      const expected = addDays(orderDate, rand(3, 30));
      await conn.execute(
        `INSERT INTO orders (product_id, supplier_id, order_date, quantity_ordered, status, expected_delivery) VALUES (?, ?, ?, ?, ?, ?)`,
        [rand(1, 200), rand(1, 50), orderDate, rand(1, 100), randItem(statuses), expected]
      );
    }
    log('✅ 5000 Orders inserted', 'success');

    log('⏳ Generating 4000 shipments...');
    for (let i = 1; i <= 4000; i++) {
      const delay = rand(-2, 15);
      await conn.execute(
        `INSERT INTO shipments (order_id, actual_delivery, shipment_status, delay_days, carrier) VALUES (?, ?, ?, ?, ?)`,
        [i, randomDate(twoYearsAgo, now), randItem(shipStatuses), Math.max(0, delay), randItem(carriers)]
      );
    }
    log('✅ 4000 Shipments inserted', 'success');
    log('🚀 All done! 9450 rows generated across 5 tables.', 'done');

  } catch (err) {
    log(`❌ Error: ${err.message}`, 'error');
  } finally {
    await conn.end();
  }
}

app.get('/', (req, res) => res.sendFile(path.join(__dirname, 'index.html')));

app.post('/generate', async (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.flushHeaders();

  const io = (msg, type = 'info') => {
    res.write(`data: ${JSON.stringify({ msg, type })}\n\n`);
  };

  await generateAll(io);
  res.write(`data: ${JSON.stringify({ msg: 'STREAM_END', type: 'end' })}\n\n`);
  res.end();
});

app.listen(3000, () => console.log('🚀 Server running at http://localhost:3000'));