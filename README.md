# Tech Playground Challenge

Welcome to the **Tech Playground Challenge**!

## Implemented by Carlos Daniel

Some shortcuts are defined in the **Makefile**. You will need **make** installed, and then you can run `make` from a terminal opened in the project root directory to see a brief help.

The chosen tasks are marked in the appropriate section.

---

## Dependencies

### Back-end (Python + FastAPI)

* **Python:** `3.11`
* **Framework & server:** `fastapi[all]`, `uvicorn[standard]`
* **Database:** `psycopg[binary]`, `psycopg2-binary`, `SQLAlchemy`, `sqlmodel`, `alembic`
* **Auth & Security:** `python-jose[cryptography]`, `passlib[bcrypt]`, `bcrypt`, `cryptography`, `zxcvbn`, `fastauth_iq`
* **HTTP & Config:** `requests`, `dynaconf`, `python-dotenv`
* **Testing:** `pytest`, `pytest-asyncio`, `pytest-cov`
* **AI / ML for Sentiment Analysis:** `transformers`, `torch`, `accelerate`, `huggingface-hub`

Install dependencies:

```bash
cd back
pip install -r requirements.txt
```

**It's recommended to use an environment such as `virtualenv` or `conda`.**

---

### Front-end (Node.js + Angular + TailwindCSS)

* **Node:** `v24.8.0`
* **Framework:** Angular 20 (`@angular/core`, `@angular/common`, `@angular/forms`, `@angular/router`)
* **Reactive & runtime support:** `rxjs`, `zone.js`
* **Styling:** `tailwindcss`, `postcss`, `@tailwindcss/postcss`
* **Dev tools:** `@angular/cli`, `typescript`, `karma`, `jasmine`

Install dependencies:

```bash
cd front
npm install
```

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/cdansantana/pinpeople-technicalcase.git
cd pinpeople-technicalcase
```

2. Install back-end dependencies:

```bash
cd back
pip install -r requirements.txt
```

3. Install front-end dependencies:

```bash
cd front
npm install
```

4. Optional: Prepare Docker environment:

```bash
make compose-up
```

---

## Running the Application

### Back-end

* Development (auto-reload):

```bash
make back-dev
```

* Production:

```bash
make back-prd
```

* Run tests with coverage:

```bash
make back-coverage
```

* Run unit/functional tests:

```bash
make back-test
```

### Front-end

* Start Angular development server:

```bash
make front-dev
```

Visit [http://localhost:8080](http://localhost:8080) to access the front-end.

---

### Using Docker

* Build and run containers:

```bash
make compose-up-build
```

* Run containers in detached mode:

```bash
make compose-up
```

* Stop containers:

```bash
make compose-down
```

* Clean containers, images, and volumes:

```bash
make compose-clear
```

* Prune Docker system:

```bash
make compose-prune
```

---

## Notes

* Requires **Python >= 3.11** and **Node.js >= 20**.
* Default database: sqlite, and with docker PostgreSQL.
* Back-end supports JWT authentication.
* For development, run `make back-dev` and `make front-dev` simultaneously.
* Use `make help` to see all available commands.

---

---

## About the Challenge

This is your opportunity to dive into a real-world dataset and create something extraordinary. Whether you're passionate about data analysis, visualization, backend development, or creative exploration, there's a task here that's perfect for you. Choose the challenges that excite you and let your skills shine!

## How to Participate

- **Choose Your Tasks**: Pick any tasks from the checklist below that spark your interest. You're free to choose as many or as few as you like.
- **Showcase Your Skills**: Focus on creating high-quality, well-thought-out solutions.
- **Use Your Favorite Tools**: Feel free to use any programming languages, frameworks, or tools you're comfortable with.

## Dataset Overview

The provided dataset (`data.csv`) contains employee feedback data with fields in Portuguese. The data includes:

- **nome** (Name)
- **email**
- **email_corporativo** (Corporate Email)
- **celular** (Mobile Phone)
- **area** (Department)
- **cargo** (Position)
- **funcao** (Function)
- **localidade** (Location)
- **tempo_de_empresa** (Company Tenure)
- **genero** (Gender)
- **geracao** (Generation)
- **n0_empresa** (Company Level 0)
- **n1_diretoria** (Directorate Level 1)
- **n2_gerencia** (Management Level 2)
- **n3_coordenacao** (Coordination Level 3)
- **n4_area** (Area Level 4)
- **Data da Resposta** (Response Date)
- **Interesse no Cargo** (Interest in Position)
- **Comentários - Interesse no Cargo** (Comments - Interest in Position)
- **Contribuição** (Contribution)
- **Comentários - Contribuição** (Comments - Contribution)
- **Aprendizado e Desenvolvimento** (Learning and Development)
- **Comentários - Aprendizado e Desenvolvimento** (Comments - Learning and Development)
- **Feedback**
- **Comentários - Feedback** (Comments - Feedback)
- **Interação com Gestor** (Interaction with Manager)
- **Comentários - Interação com Gestor** (Comments - Interaction with Manager)
- **Clareza sobre Possibilidades de Carreira** (Clarity about Career Opportunities)
- **Comentários - Clareza sobre Possibilidades de Carreira** (Comments - Clarity about Career Opportunities)
- **Expectativa de Permanência** (Expectation of Permanence)
- **Comentários - Expectativa de Permanência** (Comments - Expectation of Permanence)
- **eNPS** (Employee Net Promoter Score)
- **[Aberta] eNPS** (Open Comments - eNPS)

**Note**: Since the data is in Portuguese, you may need to handle text processing accordingly, especially for tasks involving text analysis or sentiment analysis.

## Key Concepts

This section explains key concepts related to the dataset to ensure you have a clear understanding of the terms used:

### 1. **Likert Scale**
The Likert scale is a common way to measure attitudes or opinions. Respondents are typically asked to rate their agreement or disagreement with a statement on a scale (we use a range from 1 to 5). For example:
- 1: Strongly Disagree
- 2: Disagree
- 3: Neutral
- 4: Agree
- 5: Strongly Agree

In this dataset, Likert scales are used to capture feedback on various aspects, such as career clarity, manager interaction, and learning opportunities.

---

### 2. **Favorability**
Favorability measures the percentage of positive responses to a survey question. For example:
- On a 5-point Likert scale:
  - Responses of 4 (Agree) and 5 (Strongly Agree) are considered favorable.
  - Responses of 3 (Neutral) are considered neutral.
  - Responses of 1 (Strongly Disagree) and 2 (Disagree) are considered unfavorable.

Favorability helps identify areas where employees feel positively about their experience.

---

### 3. **Net Promoter Score (NPS)**
NPS is a metric used to measure loyalty and satisfaction, often represented as a single number between -100 and 100. It is based on responses to the question: 
*"On a scale from 0 to 10, how likely are you to recommend this company as a great place to work?"*
- Respondents are categorized as:
  - **Promoters** (9-10): Loyal enthusiasts who will recommend the company.
  - **Passives** (7-8): Neutral respondents.
  - **Detractors** (0-6): Unhappy respondents who may discourage others.
- **Calculation**:  

```
NPS = (% Promoters) - (% Detractors)
```

NPS provides insight into overall employee sentiment in a scale from -100 (100% Detractors) to +100 (100% Promoters) where the higher the better.

---

### 4. **Survey Conversion**
Survey conversion refers to the percentage of employees who completed the survey out of those who were invited to participate. For example:
- If 500 employees were invited and 350 completed the survey, the conversion rate is:

```
Conversion Rate = (350 / 500) * 100 = 70%
```

A high conversion rate indicates good participation and engagement with the survey process.

---

### How These Concepts Apply
These metrics are essential to understanding the dataset and deriving actionable insights. As you work through the challenge, consider how Likert-scale responses, Favorability, NPS, and survey conversion reflect employee sentiment and help inform decision-making.

---

## Task Checklist

Select the tasks you wish to complete by marking them with an `X` in the `[ ]` brackets.

### **Your Selected Tasks**

- [X] **Task 1**: Create a Basic Database
- [X] **Task 2**: Create a Basic Dashboard
- [X] **Task 3**: Create a Test Suite
- [X] **Task 4**: Create a Docker Compose Setup
- [ ] **Task 5**: Exploratory Data Analysis
- [X] **Task 6**: Data Visualization - Company Level
- [X] **Task 7**: Data Visualization - Area Level
- [X] **Task 8**: Data Visualization - Employee Level
- [X] **Task 9**: Build a Simple API
- [X] **Task 10**: Sentiment Analysis
- [ ] **Task 11**: Report Generation
- [ ] **Task 12**: Creative Exploration

---

## Task Descriptions

### **Task 1: Create a Basic Database**

**Objective**: Design and implement a database to structure the data from the CSV file.

**Requirements**:

- Choose an appropriate database system (relational or non-relational) such as MySQL, PostgreSQL, MongoDB, etc.
- Design a schema or data model that accurately represents the data, considering the Portuguese field names.
- Write scripts or use tools to import the CSV data into the database.
- Ensure data integrity and appropriate data types for each field.
- Provide database creation scripts or configurations and instructions on how to set it up.

**Bonus**:

- Implement indexing or other optimizations for faster query performance.
- Organize the data efficiently to reduce redundancy and improve access speed.

---

### **Task 2: Create a Basic Dashboard**

**Objective**: Develop a simple dashboard to display important data insights.

**Requirements**:

- Use any frontend technology (e.g., HTML/CSS, JavaScript, React, Angular, Vue.js).
- Connect the dashboard to your database or use the CSV file directly.
- Display key metrics such as:

  - Number of employees per department (**area**).
  - Average feedback scores.
  - eNPS distribution.

- Include interactive elements like filtering by department (**area**) or position (**cargo**).
- Ensure the dashboard is user-friendly and visually appealing.

**Bonus**:

- Implement responsive design for mobile compatibility.
- Add advanced visualizations using charting libraries (e.g., D3.js, Chart.js).

---

### **Task 3: Create a Test Suite**

**Objective**: Write tests to ensure the reliability and correctness of your codebase.

**Requirements**:

- Use a testing framework relevant to your chosen language (e.g., pytest for Python, JUnit for Java, Jest for JavaScript).
- Write unit tests for key functions or components.
- Include tests for edge cases and error handling.
- Provide instructions on how to run the tests.

**Bonus**:

- Achieve high code coverage.
- Implement integration tests to test interactions between components.

---

### **Task 4: Create a Docker Compose Setup**

**Objective**: Containerize your application and its services using Docker Compose.

**Requirements**:

- Write a `Dockerfile` for your application.
- Create a `docker-compose.yml` file to define services (e.g., application server, database).
- Ensure that running `docker-compose up` sets up the entire environment.
- Provide instructions on how to build and run the containers.

**Bonus**:

- Use environment variables for configuration.
- Implement multi-stage builds to optimize image size.

---

### **Task 5: Exploratory Data Analysis**

**Objective**: Analyze the dataset to extract meaningful insights.

**Requirements**:

- Compute summary statistics (mean, median, mode, etc.) for numerical fields.
- Identify trends or patterns (e.g., average feedback scores by department (**area**)).
- Visualize key findings using charts or graphs.
- Provide a brief report summarizing your insights.

---

### **Task 6: Data Visualization - Company Level**

**Objective**: Create visualizations that provide insights at the company-wide level.

**Requirements**:

- Develop at least two visualizations that represent data across the entire company.
- Examples include:

  - Overall employee satisfaction scores.
  - Company-wide eNPS scores.
  - Distribution of company tenure among all employees.

- Ensure visualizations are clear, labeled, and easy to understand.
- Explain what each visualization reveals about the company.

**Bonus**:

- Use interactive dashboards or advanced visualization techniques.
- Incorporate time-series analysis if temporal data is available.

---

### **Task 7: Data Visualization - Area Level**

**Objective**: Create visualizations focusing on specific areas or departments within the company.

**Requirements**:

- Develop at least two visualizations that provide insights at the area or department level.
- Examples include:

  - Average feedback scores by department (**area**).
  - eNPS scores segmented by department.
  - Comparison of career expectations across different areas.

- Include interactive elements such as filtering or hovering to display more information.
- Ensure visualizations are clear, labeled, and easy to understand.
- Explain what each visualization reveals about the different areas.

**Bonus**:

- Highlight significant differences or trends between departments.
- Suggest possible reasons for observed patterns based on the data.

---

### **Task 8: Data Visualization - Employee Level**

**Objective**: Create visualizations that focus on individual employee data.

**Requirements**:

- Develop visualizations that provide insights at the employee level.
- Examples include:

  - An individual employee's feedback scores across different categories.
  - A profile visualization summarizing an employee's tenure, position, and feedback.
  - Comparison of an employee's scores to department or company averages.

- Ensure privacy considerations are met (e.g., anonymize data if necessary).
- Explain how these visualizations can be used for employee development or management.

**Bonus**:

- Create a template that can generate individual reports for any employee.
- Include recommendations or action items based on the data.

---

### **Task 9: Build a Simple API**

**Objective**: Develop an API to serve data from the dataset.

**Requirements**:

- Implement at least one endpoint that returns data in JSON format.
- Use any framework or language you're comfortable with.
- Include instructions on how to run and test the API.

**Bonus**:

- Implement multiple endpoints for different data queries.
- Include pagination or filtering options.

---

### **Task 10: Sentiment Analysis**

**Objective**: Perform sentiment analysis on the comment fields.

**Requirements**:

- Preprocess the text data (e.g., tokenization, stop-word removal).
- Use any method or library to analyze sentiment in Portuguese (e.g., NLTK with Portuguese support, spaCy with Portuguese models).
- Summarize the overall sentiment and provide examples.
- Document your approach and findings.

**Note**: Since the comments are in Portuguese, ensure that your tools and methods support processing text in Portuguese.

---

### **Task 11: Report Generation**

**Objective**: Generate a report highlighting key aspects of the data.

**Requirements**:

- Include tables, charts, or graphs to support your findings.
- Summarize important metrics like eNPS scores or feedback trends.
- The report can be in any format (PDF, Markdown, HTML).

---

### **Task 12: Creative Exploration**

**Objective**: Explore the dataset in a way that interests you.

**Requirements**:

- Pose a question or hypothesis related to the data.
- Use the data to answer the question or test the hypothesis.
- Document your process, findings, and any conclusions drawn.

---

## Getting Started

1. **Download the Dataset**: Access `data.csv` from the repository.
2. **Choose Your Adventure**: Pick the tasks that excite you and mark them in the checklist above.
3. **Create Your Masterpiece**: Develop your solutions using your preferred tools and technologies.
4. **Share Your Work**: Organize your code and documentation, and get ready to showcase what you've built.
5. **Attention**: Ensure that no sensitive information (e.g., API keys, personal data) is included in your repository.

## Submission Guidelines

- **Create a New Repository**: Use a platform such as GitHub, GitLab, or Bitbucket to host your repository.
- **Code and Files**: Include all code, scripts, and other files used in your solution.
- **README**: Provide a README file that:
  - Lists the tasks you completed.
  - Explains how to run your code and view results.
  - Discusses any assumptions or decisions you made.
- **Documentation**: Include any reports or visualizations you created.
- **Instructions**: Provide clear instructions for setting up and running your project.
- **Share you repository**: Provide the link to your repository as per the submission instructions provided.


## Let Your Creativity Flow!

This is more than just a challenge—it's a playground for your ideas. Feel free to go beyond the tasks, add your own flair, and have fun exploring the possibilities!

---

We hope you enjoy this challenge and look forward to seeing the amazing things you create. Happy coding!
