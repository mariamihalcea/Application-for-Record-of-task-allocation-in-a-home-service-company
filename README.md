# Database Project – Task Allocation Management  

## Author  
Mihalcea Maria-Alexandra  

## Description  
This application manages task allocation for employees in a home service company, offering services such as cleaning, repairs, and personal care. It assigns tasks based on employee availability, client location, and service type. The system tracks task statuses (pending, in progress, completed, canceled) and generates reports on completed tasks.  

## Features  

### Core Features  
- **Employee & Client Management**  
  - Add, edit, and delete employees and clients  
  - View employee details (name, specialization, availability)  
  - View client details (service history, location)  

- **Task Management**  
  - Create new tasks for clients  
  - Assign tasks manually or automatically based on availability and specialization  
  - Update task status (pending, in progress, completed, canceled)  

- **Scheduling Management**  
  - Schedule tasks based on employee availability  

- **Reports & Statistics**  
  - Employee performance reports (task count, average duration, evaluation)  
  - Client history reports (services received, details)  

## Database Design  

### Identified Tables  
1. **Employees** (`Angajati`)  
   - `id_angajat` (INT, PK)  
   - `nume` (VARCHAR)  
   - `prenume` (VARCHAR)  
   - `specializare` (VARCHAR)  
   - `email` (VARCHAR, UNIQUE)  
   - `disponibilitate` (BOOLEAN)  

2. **Clients** (`Clienti`)  
   - `id_client` (INT, PK)  
   - `nume` (VARCHAR)  
   - `prenume` (VARCHAR)  
   - `adresa` (VARCHAR)  
   - `telefon` (VARCHAR, UNIQUE)  
   - `email` (VARCHAR, UNIQUE)  

3. **Services** (`Servicii`)  
   - `id_serviciu` (INT, PK)  
   - `denumire` (VARCHAR)  
   - `descriere` (TEXT)  
   - `pret` (DECIMAL, CHECK > 0)  

4. **Orders** (`Comenzi`)  
   - `id_comanda` (INT, PK)  
   - `id_client` (INT, FK to Clients)  
   - `data_asignare` (DATE)  
   - `data_finalizare` (DATE)  
   - `pret_final` (DECIMAL, CHECK > 0)  

5. **Task Statuses** (`Status_task-uri`)  
   - `id_status` (INT, PK)  
   - `denumire_status` (VARCHAR)  

6. **Employee Tasks** (`Task-uri angajat`)  
   - `id_task_angajat` (INT, PK)  
   - `id_angajat` (INT, FK to Employees)  
   - `id_comanda` (INT, FK to Orders)  

7. **Order Services** (`Servicii_Comanda`)  
   - `id_comanda` (INT, FK to Orders)  
   - `id_serviciu` (INT, FK to Services)  

### Table Relationships  
- **One-to-Many Relationships:**  
  - A client can have multiple orders  
  - A task status can be linked to multiple orders  

- **Many-to-Many Relationships:**  
  - Employees and Orders: An employee can work on multiple orders, and an order can have multiple employees (via the `Employee Tasks` table)  
  - Services and Orders: An order can contain multiple services, and a service can be part of multiple orders (via the `Order Services` table)  

## Integrity Constraints  
1. **Primary Keys** – Each table has a unique ID field (`id_angajat`, `id_client`, `id_serviciu`, etc.), which auto-increments.  
2. **Unique Constraints** – Emails and phone numbers must be unique in the Clients and Employees tables.  
3. **Validation Constraints** – The `pret` (price) fields in Services and Orders must have positive values (`CHECK > 0`).  

## Application Workflow  

### 1. Login Page  
Users must log in with an employee account. The system verifies the email and password from the database.  

### 2. Employee Dashboard  
- **Employee List (`/angajat`)** – Displays all employees  
- **Delete Employee** – Remove an employee by `id_angajat`  
- **Available Employees** – Shows employees without assigned tasks  
- **Completed Tasks** – Lists tasks completed by employees  
- **Assign Task** – Add a new task for a specific employee  
- **Top Employees** – Employees who worked on high-value orders  
- **Employees Without Orders** – Employees with no assigned tasks  

### 3. Order Management  
- **Order List** – Displays all orders  
- **Add Order** – Creates a new order  
- **Calculate Order Price** – Sums up service costs for an order  

### 4. Service Management  
- **Service List** – Displays all available services  
- **Add Service** – Adds a new service  
- **Edit Service (`/update_service/<int:service_id>`)** – Modify service details  
- **Orders with Specific Services** – Shows orders that include a selected service  

### 5. Client Management  
- **Client List** – Displays all clients  
- **Add Client** – Creates a new client  
- **Edit Client** – Modifies an existing client  
- **Client Orders** – Lists orders associated with a client  
- **Clients with Multiple Services** – Clients who have ordered at least two services  


