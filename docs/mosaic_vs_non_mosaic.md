# Mosaic AI Agent Framework vs an AI Agent Without It


# Building an AI Agent Without Mosaic AI Agent Framework

When building an agent from scratch, developers are responsible for connecting all of the individual components needed to make the application work.

Typical responsibilities include:

* Selecting and connecting an LLM
* Creating prompts
* Defining tools
* Writing tool-calling logic
* Managing conversation history
* Connecting to databases
* Integrating vector search
* Handling authentication
* Deploying the application
* Monitoring usage and failures
* Evaluating model quality
* Managing logs and versioning

This approach gives complete flexibility because every part of the application can be customized. However, it also means developers must design, implement, test, and maintain every component themselves.

---

# Building an AI Agent with Mosaic AI Agent Framework

Mosaic AI Agent Framework provides a structured way to build and deploy AI agents on Databricks.

Instead of creating the surrounding infrastructure yourself, the framework provides built-in support for many common capabilities required in production AI applications.

Developers mainly focus on:

* Choosing the language model
* Writing the agent instructions
* Registering the available tools
* Defining business logic

The framework handles much of the orchestration and integrates with other Databricks services.

---

# Key Differences

| Without Mosaic AI Agent Framework                                | With Mosaic AI Agent Framework                                           |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Developers build the agent infrastructure themselves.            | The framework provides the infrastructure.                               |
| Tool integration is implemented manually.                        | Tool integration is built into the framework.                            |
| Deployment requires custom implementation.                       | Deployment is integrated with Databricks Model Serving.                  |
| Monitoring and evaluation require additional solutions.          | Monitoring and evaluation are available through Databricks capabilities. |
| Security and governance must be implemented separately.          | Integrates with Unity Catalog for governance and permissions.            |
| Vector Search integration is manual.                             | Native integration with Databricks Vector Search.                        |
| Logging and experiment tracking require additional setup.        | Works with MLflow for tracking and version management.                   |
| Authentication and access control require custom implementation. | Uses Databricks identity and access management.                          |


# When to Build Without Mosaic AI Agent Framework

Building an agent without Mosaic AI Agent Framework may be appropriate when:

* The application is a prototype or proof of concept.
* The project is not running on Databricks.
* A highly customized architecture is required.
* The development team prefers to manage every component independently.

---

# When to Use Mosaic AI Agent Framework

Mosaic AI Agent Framework is generally a good choice when:

* Data is stored in Databricks.
* Unity Catalog is used for data governance.
* Production deployment is required.
* Monitoring and evaluation are important.
* Security and governance must be managed centrally.
* The application needs to integrate with Databricks services such as Vector Search, MLflow, Model Serving, and AI Gateway.

---



| Feature          | Plain Python / LangChain/ LangGraph | Mosaic AI Agent Framework |
| ---------------- | ------------------------ | ------------------------- |
| LLM              | ✅                        | ✅                         |
| Prompt           | Manual                   | Managed                   |
| Tool Calling     | Manual                   | Built-in                  |
| UC Functions     | Manual integration       | Native                    |
| Vector Search    | Manual                   | Native                    |
| MLflow           | Manual                   | Native                    |
| Deployment       | Manual APIs              | One-click serving         |
| Evaluation       | Build yourself           | Built-in                  |
| Monitoring       | Build yourself           | Built-in                  |
| Governance       | Custom                   | Unity Catalog integration |
| Authentication   | Custom                   | Databricks-managed        |
| AI Gateway       | Separate setup           | Integrated                |
| Production Ready | More engineering effort  | Designed for enterprise   |
