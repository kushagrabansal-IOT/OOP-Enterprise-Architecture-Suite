"""
OOP-Enterprise-Architecture-Suite — ERP System
Complete OOP Architecture: SOLID + Design Patterns + Layered Architecture
Modules: Employee, Inventory, Finance, Customer, Reporting
Author : Kushagra Bansal — Project Lab India
Run    : python main.py
"""
from abc import ABC, abstractmethod
from datetime import datetime, date
from enum import Enum
from typing import List, Optional, Dict
import uuid

# ════════════════════════════════════════════════════════════
# LAYER 1: DOMAIN MODELS (Pure OOP Entities)
# ════════════════════════════════════════════════════════════

class Department(Enum):
    ENGINEERING = "Engineering"; SALES = "Sales"
    FINANCE = "Finance"; HR = "Human Resources"; OPERATIONS = "Operations"

class EmployeeStatus(Enum):
    ACTIVE = "Active"; ON_LEAVE = "On Leave"; RESIGNED = "Resigned"

class InvoiceStatus(Enum):
    DRAFT="Draft"; SENT="Sent"; PAID="Paid"; OVERDUE="Overdue"; CANCELLED="Cancelled"

class Entity(ABC):
    """Base entity with ID and audit timestamps"""
    def __init__(self):
        self.id         = str(uuid.uuid4())[:8].upper()
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def _touch(self):
        self.updated_at = datetime.now()


class Employee(Entity):
    def __init__(self, name, email, department, role, salary, manager_id=None):
        super().__init__()
        self.__name       = name
        self.__email      = email
        self.__department = department
        self.__role       = role
        self.__salary     = salary
        self.__manager_id = manager_id
        self.__status     = EmployeeStatus.ACTIVE
        self.__leave_balance = 21
        self.__skills     = []

    @property
    def name(self):         return self.__name
    @property
    def email(self):        return self.__email
    @property
    def department(self):   return self.__department
    @property
    def role(self):         return self.__role
    @property
    def salary(self):       return self.__salary
    @property
    def status(self):       return self.__status
    @property
    def leave_balance(self):return self.__leave_balance

    def give_raise(self, amount):
        if amount <= 0: raise ValueError("Raise must be positive")
        self.__salary += amount
        self._touch()
        print(f"  💰 {self.__name} salary: ₹{self.__salary-amount:,.0f} → ₹{self.__salary:,.0f}")

    def apply_leave(self, days):
        if days > self.__leave_balance:
            raise ValueError(f"Insufficient leave balance: {self.__leave_balance} days")
        self.__leave_balance -= days
        self.__status = EmployeeStatus.ON_LEAVE if days > 0 else EmployeeStatus.ACTIVE
        self._touch()

    def add_skill(self, skill):
        if skill not in self.__skills: self.__skills.append(skill)

    def get_skills(self): return self.__skills.copy()

    def resign(self):
        self.__status = EmployeeStatus.RESIGNED
        self._touch()
        print(f"  👋 {self.__name} has resigned")

    def __str__(self):
        return f"Employee[{self.id}] {self.__name} | {self.__role} | {self.__department.value} | ₹{self.__salary:,.0f}"


class Product(Entity):
    def __init__(self, name, sku, price, cost, stock, category, reorder_point=10):
        super().__init__()
        self.name          = name
        self.sku           = sku
        self.__price       = price
        self.__cost        = cost
        self.__stock       = stock
        self.category      = category
        self.reorder_point = reorder_point

    @property
    def price(self):   return self.__price
    @property
    def cost(self):    return self.__cost
    @property
    def stock(self):   return self.__stock
    @property
    def margin(self):  return round((self.__price - self.__cost) / self.__price * 100, 2)
    @property
    def low_stock(self): return self.__stock <= self.reorder_point

    def update_price(self, new_price):
        if new_price <= 0: raise ValueError("Price must be positive")
        old = self.__price; self.__price = new_price; self._touch()
        print(f"  💲 {self.name} price: ₹{old:,.2f} → ₹{new_price:,.2f}")

    def add_stock(self, qty):
        self.__stock += qty; self._touch()

    def deduct_stock(self, qty):
        if qty > self.__stock: raise ValueError(f"Insufficient stock: {self.__stock}")
        self.__stock -= qty; self._touch()

    def __str__(self):
        low = " ⚠️ LOW STOCK" if self.low_stock else ""
        return f"Product[{self.sku}] {self.name} | ₹{self.__price:,.2f} | Stock:{self.__stock}{low}"


class Customer(Entity):
    def __init__(self, name, email, phone, company="", gstin=""):
        super().__init__()
        self.name    = name
        self.email   = email
        self.phone   = phone
        self.company = company
        self.gstin   = gstin
        self.__credit_limit = 100000
        self.__outstanding  = 0.0

    @property
    def credit_limit(self): return self.__credit_limit
    @property
    def outstanding(self):  return self.__outstanding
    @property
    def available_credit(self): return self.__credit_limit - self.__outstanding

    def set_credit_limit(self, limit):
        self.__credit_limit = limit

    def add_outstanding(self, amount):
        if self.__outstanding + amount > self.__credit_limit:
            raise ValueError(f"Credit limit ₹{self.__credit_limit:,.2f} exceeded")
        self.__outstanding += amount

    def clear_outstanding(self, amount):
        self.__outstanding = max(0, self.__outstanding - amount)

    def __str__(self):
        return f"Customer[{self.id}] {self.name} | {self.company} | Outstanding: ₹{self.__outstanding:,.2f}"


class InvoiceItem:
    def __init__(self, product, qty, unit_price):
        self.product    = product
        self.qty        = qty
        self.unit_price = unit_price
        self.tax_rate   = 0.18

    @property
    def subtotal(self): return self.unit_price * self.qty
    @property
    def tax(self):      return self.subtotal * self.tax_rate
    @property
    def total(self):    return self.subtotal + self.tax


class Invoice(Entity):
    def __init__(self, customer, employee, due_days=30):
        super().__init__()
        self.invoice_no = f"INV-{datetime.now().strftime('%Y%m%d')}-{self.id}"
        self.customer   = customer
        self.employee   = employee
        self.issue_date = date.today()
        self.due_date   = date.fromordinal(date.today().toordinal() + due_days)
        self.__items    = []
        self.__status   = InvoiceStatus.DRAFT
        self.__payments = []

    @property
    def items(self):    return self.__items.copy()
    @property
    def status(self):   return self.__status
    @property
    def subtotal(self): return sum(i.subtotal for i in self.__items)
    @property
    def total_tax(self):return sum(i.tax for i in self.__items)
    @property
    def total(self):    return sum(i.total for i in self.__items)
    @property
    def paid_amount(self): return sum(self.__payments)
    @property
    def balance_due(self): return self.total - self.paid_amount

    def add_item(self, product, qty):
        item = InvoiceItem(product, qty, product.price)
        self.__items.append(item)
        self._touch()

    def send(self):
        if not self.__items: raise ValueError("Cannot send empty invoice")
        self.__status = InvoiceStatus.SENT
        self.customer.add_outstanding(self.total)
        self._touch()

    def record_payment(self, amount):
        self.__payments.append(amount)
        self.customer.clear_outstanding(amount)
        if self.balance_due <= 0:
            self.__status = InvoiceStatus.PAID
        self._touch()
        print(f"  💰 Payment ₹{amount:,.2f} recorded for {self.invoice_no}")

    def print_invoice(self):
        print(f"\n  {'═'*60}")
        print(f"  INVOICE: {self.invoice_no}")
        print(f"  {'═'*60}")
        print(f"  Customer : {self.customer.name} | {self.customer.company}")
        print(f"  GST No   : {self.customer.gstin or 'N/A'}")
        print(f"  Date     : {self.issue_date} | Due: {self.due_date}")
        print(f"  Status   : {self.__status.value}")
        print(f"  {'─'*60}")
        print(f"  {'PRODUCT':<25} {'QTY':>4} {'RATE':>10} {'SUBTOTAL':>12} {'TAX':>8} {'TOTAL':>12}")
        print(f"  {'─'*60}")
        for item in self.__items:
            print(f"  {item.product.name:<25} {item.qty:>4} ₹{item.unit_price:>9,.2f}"
                  f" ₹{item.subtotal:>11,.2f} ₹{item.tax:>7,.2f} ₹{item.total:>11,.2f}")
        print(f"  {'─'*60}")
        print(f"  {'Subtotal':>53}: ₹{self.subtotal:>10,.2f}")
        print(f"  {'GST (18%)':>53}: ₹{self.total_tax:>10,.2f}")
        print(f"  {'TOTAL':>53}: ₹{self.total:>10,.2f}")
        if self.paid_amount:
            print(f"  {'Paid':>53}: ₹{self.paid_amount:>10,.2f}")
            print(f"  {'Balance Due':>53}: ₹{self.balance_due:>10,.2f}")
        print(f"  {'═'*60}")


# ════════════════════════════════════════════════════════════
# LAYER 2: REPOSITORY (Data Access Layer)
# ════════════════════════════════════════════════════════════

class Repository(ABC):
    def __init__(self):
        self._store: Dict[str, Entity] = {}

    def save(self, entity: Entity):
        self._store[entity.id] = entity

    def get(self, id: str) -> Optional[Entity]:
        return self._store.get(id)

    def list_all(self) -> List[Entity]:
        return list(self._store.values())

    def delete(self, id: str) -> bool:
        if id in self._store:
            del self._store[id]; return True
        return False

    def count(self) -> int:
        return len(self._store)

class EmployeeRepository(Repository):
    def find_by_department(self, dept: Department):
        return [e for e in self._store.values()
                if isinstance(e, Employee) and e.department == dept]

    def find_by_status(self, status: EmployeeStatus):
        return [e for e in self._store.values()
                if isinstance(e, Employee) and e.status == status]

class ProductRepository(Repository):
    def find_low_stock(self):
        return [p for p in self._store.values()
                if isinstance(p, Product) and p.low_stock]

    def find_by_category(self, category):
        return [p for p in self._store.values()
                if isinstance(p, Product) and p.category == category]

class CustomerRepository(Repository):
    def find_by_company(self, company):
        return [c for c in self._store.values()
                if isinstance(c, Customer) and company.lower() in c.company.lower()]

class InvoiceRepository(Repository):
    def find_by_status(self, status: InvoiceStatus):
        return [i for i in self._store.values()
                if isinstance(i, Invoice) and i.status == status]

    def get_total_revenue(self):
        return sum(i.paid_amount for i in self._store.values()
                   if isinstance(i, Invoice) and i.status == InvoiceStatus.PAID)


# ════════════════════════════════════════════════════════════
# LAYER 3: SERVICE LAYER (Business Logic)
# ════════════════════════════════════════════════════════════

class EmployeeService:
    def __init__(self, repo: EmployeeRepository):
        self._repo = repo

    def hire(self, name, email, dept, role, salary, manager_id=None) -> Employee:
        emp = Employee(name, email, dept, role, salary, manager_id)
        self._repo.save(emp)
        print(f"  ✅ Hired: {emp}")
        return emp

    def process_payroll(self) -> dict:
        employees = self._repo.find_by_status(EmployeeStatus.ACTIVE)
        total = sum(e.salary for e in employees)
        print(f"\n  📋 PAYROLL SUMMARY")
        print(f"  Active employees: {len(employees)}")
        print(f"  Total monthly payroll: ₹{total:,.2f}")
        by_dept = {}
        for e in employees:
            dept = e.department.value
            by_dept[dept] = by_dept.get(dept, 0) + e.salary
        for dept, amt in sorted(by_dept.items()):
            print(f"    {dept}: ₹{amt:,.2f}")
        return {"total":total,"count":len(employees),"by_dept":by_dept}

    def get_department_headcount(self):
        return {dept.value: len(self._repo.find_by_department(dept))
                for dept in Department}


class InventoryService:
    def __init__(self, repo: ProductRepository):
        self._repo = repo

    def add_product(self, name, sku, price, cost, stock, category) -> Product:
        p = Product(name, sku, price, cost, stock, category)
        self._repo.save(p)
        return p

    def restock(self, product_id, qty):
        p = self._repo.get(product_id)
        if not p: raise ValueError(f"Product {product_id} not found")
        p.add_stock(qty)
        print(f"  📦 Restocked {p.name}: +{qty} units")

    def get_low_stock_alert(self):
        low = self._repo.find_low_stock()
        if low:
            print(f"\n  ⚠️  LOW STOCK ALERT ({len(low)} items):")
            for p in low: print(f"    {p}")
        return low

    def get_inventory_value(self):
        products = self._repo.list_all()
        return sum(p.stock * p.cost for p in products if isinstance(p, Product))


class FinanceService:
    def __init__(self, invoice_repo: InvoiceRepository, product_repo: ProductRepository):
        self._inv_repo  = invoice_repo
        self._prod_repo = product_repo

    def create_invoice(self, customer, employee, items_data) -> Invoice:
        inv = Invoice(customer, employee)
        for product_id, qty in items_data:
            p = self._prod_repo.get(product_id)
            if not p: raise ValueError(f"Product {product_id} not found")
            p.deduct_stock(qty)
            inv.add_item(p, qty)
        self._inv_repo.save(inv)
        return inv

    def get_financial_summary(self):
        all_invoices = self._inv_repo.list_all()
        revenue      = self._inv_repo.get_total_revenue()
        pending      = sum(i.balance_due for i in all_invoices
                          if isinstance(i,Invoice) and i.status == InvoiceStatus.SENT)
        print(f"\n  💹 FINANCIAL SUMMARY")
        print(f"  Total Revenue (Collected): ₹{revenue:,.2f}")
        print(f"  Pending Receivables:       ₹{pending:,.2f}")
        print(f"  Total Invoices:            {len(all_invoices)}")
        return {"revenue":revenue,"pending":pending}


# ════════════════════════════════════════════════════════════
# LAYER 4: REPORTING ENGINE
# ════════════════════════════════════════════════════════════

class ReportFormat(Enum):
    CONSOLE="console"; CSV="csv"; JSON="json"

class ReportEngine:
    def __init__(self, emp_svc, inv_svc, fin_svc):
        self._emp = emp_svc
        self._inv = inv_svc
        self._fin = fin_svc

    def generate_erp_dashboard(self):
        print(f"\n{'═'*65}")
        print(f"  🏢 ERP DASHBOARD — Project Lab India")
        print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'═'*65}")
        self._emp.process_payroll()
        print()
        low_stock = self._inv.get_low_stock_alert()
        inv_value = self._inv.get_inventory_value()
        print(f"\n  📦 Total Inventory Value: ₹{inv_value:,.2f}")
        self._fin.get_financial_summary()
        print(f"{'═'*65}")


# ════════════════════════════════════════════════════════════
# LAYER 5: APPLICATION ENTRY POINT (DI Container)
# ════════════════════════════════════════════════════════════

class ERPApplication:
    """Wires everything together — Dependency Injection Container"""

    def __init__(self):
        # Repositories
        self.emp_repo  = EmployeeRepository()
        self.prod_repo = ProductRepository()
        self.cust_repo = CustomerRepository()
        self.inv_repo  = InvoiceRepository()

        # Services (injected with repositories)
        self.emp_svc   = EmployeeService(self.emp_repo)
        self.inv_svc   = InventoryService(self.prod_repo)
        self.fin_svc   = FinanceService(self.inv_repo, self.prod_repo)

        # Reporting
        self.reports   = ReportEngine(self.emp_svc, self.inv_svc, self.fin_svc)

    def seed_data(self):
        """Seed demo data"""
        print("\n── Seeding Demo Data ──")

        # Employees
        ceo   = self.emp_svc.hire("Kushagra Bansal","kb@pli.in",Department.ENGINEERING,"CEO",250000)
        cto   = self.emp_svc.hire("Priya Sharma","ps@pli.in",Department.ENGINEERING,"CTO",200000,ceo.id)
        sales = self.emp_svc.hire("Rahul Verma","rv@pli.in",Department.SALES,"Sales Manager",80000,ceo.id)
        eng1  = self.emp_svc.hire("Amit Kumar","ak@pli.in",Department.ENGINEERING,"Senior Dev",120000,cto.id)
        eng2  = self.emp_svc.hire("Sunita Devi","sd@pli.in",Department.ENGINEERING,"Dev",80000,cto.id)
        for e in [cto, eng1, eng2]: e.add_skill("Python"); e.add_skill("IoT")
        eng1.give_raise(10000)

        # Products
        p1 = self.inv_svc.add_product("ESP32 DevKit","SKU001",450,200,500,"IoT Hardware")
        p2 = self.inv_svc.add_product("DHT22 Sensor","SKU002",120,60,8,"IoT Hardware")  # Low stock
        p3 = self.inv_svc.add_product("OLED Display","SKU003",200,90,150,"IoT Hardware")
        p4 = self.inv_svc.add_product("IoT Starter Kit","SKU004",2500,1200,50,"Kits")
        p5 = self.inv_svc.add_product("GSM Module","SKU005",350,180,200,"IoT Hardware")

        # Customers
        c1 = Customer("Raj Electronics","raj@re.in","9876500001","Raj Electronics Ltd","29ABCDE1234F1Z5")
        c2 = Customer("TechMakers Hub", "info@tm.in","9876500002","TechMakers Pvt Ltd","")
        self.cust_repo.save(c1); self.cust_repo.save(c2)

        # Invoices
        inv1 = self.fin_svc.create_invoice(c1, sales, [(p1.id,10),(p3.id,5)])
        inv1.send()
        inv1.print_invoice()
        inv1.record_payment(inv1.total)

        inv2 = self.fin_svc.create_invoice(c2, sales, [(p4.id,3),(p5.id,5)])
        inv2.send()

        return {"employees":5, "products":5, "customers":2, "invoices":2}


if __name__ == "__main__":
    print("═"*65)
    print("  OOP Enterprise Architecture Suite")
    print("  ERP System — Project Lab India")
    print("  Author: Kushagra Bansal")
    print("═"*65)

    app = ERPApplication()
    summary = app.seed_data()
    app.reports.generate_erp_dashboard()

    print("\n── Architecture Demonstration ──")
    print(f"  ✅ Entities:     Employee, Product, Customer, Invoice")
    print(f"  ✅ Repositories: EmployeeRepo, ProductRepo, CustomerRepo, InvoiceRepo")
    print(f"  ✅ Services:     EmployeeService, InventoryService, FinanceService")
    print(f"  ✅ Reporting:    ReportEngine (aggregates all services)")
    print(f"  ✅ DI Container: ERPApplication wires dependencies")
    print(f"  ✅ Patterns:     Repository, Service Layer, Dependency Injection")
    print(f"  ✅ SOLID:        All 5 principles demonstrated")
    print(f"\n  Seeded: {summary}")
