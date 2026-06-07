from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, func, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta, date
from jose import JWTError, jwt
import hashlib, hmac, os, random

# ── Config ────────────────────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/dashboard_db")
SECRET_KEY   = os.getenv("SECRET_KEY", "analytix-secret-key-2024")
ALGORITHM    = "HS256"

engine       = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base         = declarative_base()

app = FastAPI(title="AnalytiX API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# ── Models ────────────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"
    id       = Column(Integer, primary_key=True)
    name     = Column(String(100))
    email    = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

class Category(Base):
    __tablename__ = "categories"
    id       = Column(Integer, primary_key=True)
    name     = Column(String(100))
    slug     = Column(String(100), unique=True)
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"
    id          = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    name        = Column(String(255))
    sku         = Column(String(50), unique=True)
    price       = Column(Float)
    cost        = Column(Float, nullable=True)
    stock       = Column(Integer, default=0)
    is_active   = Column(Boolean, default=True)
    category    = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")

class Customer(Base):
    __tablename__ = "customers"
    id         = Column(Integer, primary_key=True)
    first_name = Column(String(100))
    last_name  = Column(String(100))
    email      = Column(String(255), unique=True)
    city       = Column(String(100), nullable=True)
    orders     = relationship("Order", back_populates="customer")

class Order(Base):
    __tablename__ = "orders"
    id          = Column(Integer, primary_key=True)
    reference   = Column(String(50), unique=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    status      = Column(String(50), default="pending")
    subtotal    = Column(Float, default=0)
    tax         = Column(Float, default=0)
    shipping    = Column(Float, default=0)
    total       = Column(Float, default=0)
    ordered_at  = Column(DateTime, default=datetime.utcnow)
    customer    = relationship("Customer", back_populates="orders")
    items       = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    id          = Column(Integer, primary_key=True)
    order_id    = Column(Integer, ForeignKey("orders.id"))
    product_id  = Column(Integer, ForeignKey("products.id"))
    quantity    = Column(Integer)
    unit_price  = Column(Float)
    total_price = Column(Float)
    order       = relationship("Order", back_populates="items")
    product     = relationship("Product", back_populates="order_items")

# ── DB ────────────────────────────────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── Security ──────────────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain: str, hashed: str) -> bool:
    return hmac.compare_digest(hashlib.sha256(plain.encode()).hexdigest(), hashed)

def create_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        user  = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ── Schemas ───────────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    class Config: from_attributes = True

class TokenResponse(BaseModel):
    token: str
    user: UserOut

# ── Seed ─────────────────────────────────────────────────────────────────────
def seed_data(db: Session):
    if db.query(User).first():
        return

    # Admin
    db.add(User(name="Admin", email="admin@demo.com", password=hash_password("password")))

    # Categories
    cat_names = ["Electronics", "Clothing", "Books", "Sports", "Home"]
    cats = []
    for n in cat_names:
        c = Category(name=n, slug=n.lower())
        db.add(c)
        cats.append(c)
    db.flush()

    # Products
    products_data = [
        ("Laptop Pro", "LAP-001", 8999, 6000, 25),
        ("Wireless Mouse", "MOU-001", 299, 150, 120),
        ("USB-C Hub", "HUB-001", 449, 200, 80),
        ("Keyboard", "KEY-001", 799, 400, 60),
        ("Running Shoes", "SHO-001", 699, 350, 45),
        ("Yoga Mat", "YOG-001", 249, 100, 90),
        ("Water Bottle", "BOT-001", 129, 50, 200),
        ("Backpack", "BAG-001", 599, 250, 35),
        ("Python Book", "BOK-001", 199, 80, 50),
        ("Clean Code", "BOK-002", 249, 100, 40),
    ]
    prods = []
    for name, sku, price, cost, stock in products_data:
        p = Product(category_id=random.choice(cats).id, name=name, sku=sku, price=price, cost=cost, stock=stock)
        db.add(p)
        prods.append(p)
    db.flush()

    # Customers
    first_names = ["Youssef","Fatima","Mohamed","Aicha","Omar","Sara","Karim","Nadia"]
    last_names  = ["Alami","Bennani","Chraibi","Drissi","El Fassi","Guerraoui"]
    cities      = ["Casablanca","Rabat","Marrakech","Fès","Tanger","Agadir"]
    customers   = []
    for i in range(50):
        c = Customer(
            first_name=random.choice(first_names),
            last_name=random.choice(last_names),
            email=f"client{i}@demo.com",
            city=random.choice(cities)
        )
        db.add(c)
        customers.append(c)
    db.flush()

    # Orders
    statuses = ["pending","processing","shipped","delivered","delivered","delivered","cancelled"]
    import uuid
    for i in range(300):
        days_ago   = random.randint(0, 90)
        ordered_at = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0,23))
        customer   = random.choice(customers)
        status     = random.choice(statuses)
        shipping   = 0 if random.random() > 0.5 else 39
        order = Order(
            reference=f"ORD-{uuid.uuid4().hex[:8].upper()}",
            customer_id=customer.id,
            status=status,
            shipping=shipping,
            ordered_at=ordered_at
        )
        db.add(order)
        db.flush()

        subtotal = 0
        for product in random.sample(prods, random.randint(1, 4)):
            qty   = random.randint(1, 3)
            total = qty * product.price
            subtotal += total
            db.add(OrderItem(order_id=order.id, product_id=product.id, quantity=qty, unit_price=product.price, total_price=total))

        tax = round(subtotal * 0.20, 2)
        order.subtotal = subtotal
        order.tax      = tax
        order.total    = subtotal + tax + shipping

    db.commit()
    print("✅ Database seeded!")

# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
def startup():
    import time
    for i in range(10):
        try:
            Base.metadata.create_all(bind=engine)
            db = SessionLocal()
            seed_data(db)
            db.close()
            print("✅ Database ready!")
            break
        except Exception as e:
            print(f"⏳ Waiting for DB... ({i+1}/10): {e}")
            time.sleep(3)

# ── Auth Routes ───────────────────────────────────────────────────────────────
@app.post("/api/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({"sub": user.email})
    return {"token": token, "user": user}

@app.post("/api/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(name=payload.name, email=payload.email, password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_token({"sub": user.email})
    return {"token": token, "user": user}

@app.get("/api/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user

# ── Dashboard Routes ──────────────────────────────────────────────────────────
@app.get("/api/dashboard/kpis")
def kpis(period: int = 30, db: Session = Depends(get_db), _=Depends(get_current_user)):
    now   = datetime.utcnow()
    start = now - timedelta(days=period)
    prev  = start - timedelta(days=period)

    def get_stats(s, e):
        q = db.query(Order).filter(Order.status != "cancelled", Order.ordered_at.between(s, e))
        rev = sum(o.total for o in q.all())
        cnt = q.count()
        cus = db.query(Order.customer_id).filter(Order.status != "cancelled", Order.ordered_at.between(s, e)).distinct().count()
        avg = round(rev / cnt, 2) if cnt > 0 else 0
        return rev, cnt, cus, avg

    r, o, c, a   = get_stats(start, now)
    pr, po, pc, pa = get_stats(prev, start)

    def pct(old, new):
        if old == 0: return 100 if new > 0 else 0
        return round(((new - old) / old) * 100, 1)

    return {
        "revenue":   {"value": round(r, 2), "change": pct(pr, r),  "label": "Total Revenu",   "prefix": "MAD"},
        "orders":    {"value": o,            "change": pct(po, o),  "label": "Commandes"},
        "customers": {"value": c,            "change": pct(pc, c),  "label": "Clients actifs"},
        "avg_order": {"value": a,            "change": pct(pa, a),  "label": "Panier moyen",   "prefix": "MAD"},
    }

@app.get("/api/dashboard/revenue-chart")
def revenue_chart(period: int = 30, db: Session = Depends(get_db), _=Depends(get_current_user)):
    start  = datetime.utcnow() - timedelta(days=period)
    orders = db.query(Order).filter(Order.status != "cancelled", Order.ordered_at >= start).all()
    by_day = {}
    for o in orders:
        day = o.ordered_at.strftime("%Y-%m-%d")
        if day not in by_day:
            by_day[day] = {"period": day, "revenue": 0, "orders": 0}
        by_day[day]["revenue"] += o.total
        by_day[day]["orders"]  += 1
    return sorted(by_day.values(), key=lambda x: x["period"])

@app.get("/api/dashboard/orders-by-status")
def orders_by_status(db: Session = Depends(get_db), _=Depends(get_current_user)):
    results = db.query(Order.status, func.count(Order.id)).group_by(Order.status).all()
    return [{"status": s, "count": c, "label": s.capitalize()} for s, c in results]

@app.get("/api/dashboard/top-products")
def top_products(db: Session = Depends(get_db), _=Depends(get_current_user)):
    start = datetime.utcnow() - timedelta(days=30)
    items = db.query(OrderItem).join(Order).filter(Order.status != "cancelled", Order.ordered_at >= start).all()
    by_product = {}
    for item in items:
        pid = item.product_id
        if pid not in by_product:
            by_product[pid] = {"name": item.product.name, "units_sold": 0, "revenue": 0}
        by_product[pid]["units_sold"] += item.quantity
        by_product[pid]["revenue"]    += item.total_price
    return sorted(by_product.values(), key=lambda x: x["revenue"], reverse=True)[:10]

@app.get("/api/dashboard/sales-by-category")
def sales_by_category(db: Session = Depends(get_db), _=Depends(get_current_user)):
    items = db.query(OrderItem).join(Order).filter(Order.status != "cancelled").all()
    by_cat = {}
    for item in items:
        cat = item.product.category.name if item.product.category else "Other"
        if cat not in by_cat:
            by_cat[cat] = {"category": cat, "revenue": 0}
        by_cat[cat]["revenue"] += item.total_price
    return sorted(by_cat.values(), key=lambda x: x["revenue"], reverse=True)

@app.get("/api/dashboard/recent-orders")
def recent_orders(db: Session = Depends(get_db), _=Depends(get_current_user)):
    orders = db.query(Order).order_by(Order.ordered_at.desc()).limit(10).all()
    return [{
        "id": o.id, "reference": o.reference,
        "customer": f"{o.customer.first_name} {o.customer.last_name}",
        "status": o.status, "total": o.total,
        "ordered_at": o.ordered_at.strftime("%Y-%m-%d %H:%M")
    } for o in orders]

@app.get("/health")
def health():
    return {"status": "ok"}
