# Enterprise Architecture Notes

## Layered Architecture
Layer 1: Domain Models (entities, value objects)
Layer 2: Repository Layer (data access)
Layer 3: Service Layer (business logic)
Layer 4: Reporting/Presentation
Layer 5: Application/DI Container

## Repository Pattern
Abstracts data storage from business logic.
Business code works with Repository interface.
Swap InMemory → PostgreSQL → MongoDB without changing services.

## Service Layer
Orchestrates multiple repositories.
Contains business rules.
Transactional boundary.

## Dependency Injection
Dependencies passed in constructor (DI pattern).
High-level modules don't create their own dependencies.
Enables unit testing with mock repositories.

## Interview Questions
1. What is layered architecture? Benefits?
2. What is the Repository pattern? Why use it?
3. What is a Service layer? How does it differ from Repository?
4. Explain Dependency Injection vs Dependency Inversion.
5. How would you scale this ERP to a microservices architecture?
6. What is a Domain Model vs Anemic Domain Model?
7. How do you handle transactions across multiple repositories?
