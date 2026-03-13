## **System Documentation**

## **1\. Overview**

The system is designed to allow users to upload regulatory or domain-related PDF documents along with basic metadata. These documents are securely stored in an object storage system while the metadata is stored in a relational database.

The architecture separates **file storage** and **structured data storage**, ensuring scalability, reliability, and efficient document management.

This system supports the following key functions:

* Capture document metadata

* Upload and store PDF files

* Maintain a link between stored files and database records

---

# **2\. Core Components**

The system consists of three primary layers.

### **1\. Frontend Application**

The frontend provides the user interface where users submit document information and upload files.

The interface captures the following details:

* Subdomain (for example: SEBI, RBI, IRDA)

* Document Title

* Issue Date

* PDF File Upload

Once the user submits the form, the frontend sends the request to the backend service.

---

### **2\. Backend Service**

The backend acts as the central processing unit of the system. Its responsibilities include:

* Receiving upload requests from the frontend

* Validating user input

* Uploading files to object storage

* Storing metadata in the database

* Maintaining the relationship between the file and its metadata

The backend ensures that each document stored in the system can be uniquely identified and retrieved.

---

### **3\. Storage Layer**

The system uses two storage mechanisms.

#### **Object Storage (MinIO)**

MinIO is used to store the actual PDF files. Object storage is optimized for storing large binary files such as documents, images, and videos.

Benefits of using object storage:

* Scalable file storage

* Efficient handling of large files

* Independent from database growth

* Secure file management

Each uploaded document is saved with a structured storage path to ensure organization.

---

#### **Relational Database (SQL Database)**

The relational database stores metadata related to each document. This includes:

* Document identifier

* Subdomain classification

* Title

* Issue date

* File location reference

* Upload timestamps

The database does not store the actual document but instead stores a reference to the file stored in object storage.

---

# **3\. Metadata and File Linking**

A key part of the system is maintaining a link between the database record and the stored file.

This is achieved using a **file reference or object key**.

The object key represents the location of the file inside the object storage system.

Example concept:

Document Record → Contains file reference → Points to file in storage.

This approach allows:

* Efficient querying of document metadata

* Fast file retrieval

* Reduced database storage usage

---

# **4\. System Workflow**

The document upload process follows a sequential workflow.

### **Step 1 — User Input**

The user opens the document upload interface and provides the required information:

* Selects a subdomain

* Enters the document title

* Selects the issue date

* Uploads the PDF document

---

### **Step 2 — Request Submission**

After the form is submitted, the frontend sends the data to the backend service.

The request includes both metadata and the document file.

---

### **Step 3 — Validation**

The backend validates the request to ensure:

* All required fields are provided

* The uploaded file is a valid PDF

* File size limits are respected

---

### **Step 4 — File Storage**

Once validated, the backend uploads the document to the object storage system.

The storage system assigns a unique location for the file.

---

### **Step 5 — Metadata Storage**

After the file is successfully stored, the backend records the document metadata in the database.

The metadata record includes the reference to the stored file.

---

### **Step 6 — Response to User**

The backend returns a success response to the frontend, confirming that the document has been uploaded and stored.

---

# **5\. Workflow Diagram**

Document Upload Workflow

User  
│  
│ Fill Document Form  
│  
▼  
Frontend Application  
│  
│ Submit Upload Request  
│  
▼  
Backend Service  
│  
├── Validate Input Data  
│  
├── Store PDF in Object Storage  
│  
├── Generate File Reference  
│  
└── Save Metadata in Database  
│  
▼  
Upload Confirmation  
│  
▼  
User Notification  
---

# **6\. System Architecture**

The system follows a layered architecture where each component has a distinct responsibility.

               ┌─────────────────────┐  
               │     User Interface                          │  
               │      (Frontend)                               │  
               └───────────┬─────────┘  
                           │  
                           │ API Requests  
                           ▼  
               ┌─────────────────────┐  
               │    Backend Service                       │  
               │  Request Processing                    │  
               └───────────┬─────────┘  
                                              │  
               ┌───────────┴───────────┐  
               │                            │  
               ▼                          ▼  
       ┌───────────────┐       ┌───────────────┐  
       │  Object Store                 │       │  SQL Database            │  
       │     (MinIO)                      │       │  Metadata                     │  
       └───────────────┘       └───────────────┘  
                │  
               ▼  
         Stored PDF Files  
---

# **7\. Data Flow Architecture**

The system separates **file storage** and **metadata storage** to maintain scalability.

User Upload  
    │  
    ▼  
Frontend Application  
    │  
    ▼  
Backend Processing  
    │  
    ├───────────────► Object Storage  
    │                   (Stores PDF)  
    │  
    └───────────────► Database  
                        (Stores Metadata)  
---

# **8\. Benefits of the Architecture**

### **Scalability**

Separating file storage from database storage allows the system to scale efficiently as document volume increases.

---

### **Performance**

Databases perform better when storing structured data rather than large files.

Object storage systems are optimized for handling large documents.

---

### **Maintainability**

The architecture allows independent upgrades and scaling of:

* Storage system

* Database

* Backend services

---

### **Future Extensibility**

The system is designed to support additional processing steps such as:

* OCR extraction

* AI document analysis

* Document indexing

* Search capabilities

---

# **9\. Conclusion** 

This system provides a robust and scalable architecture for managing uploaded documents and associated metadata.

By separating file storage from relational data storage, the system ensures:

* Efficient storage management

* High performance

* Easy integration with future AI workflows

The design also ensures that each document can be easily retrieved, processed, and extended for advanced applications.

