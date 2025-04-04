# ForgeAI RAG System User Guide

## Introduction

The RAG (Retrieval-Augmented Generation) system by ForgeAI allows you to enhance your generative AI applications by enriching them with your own data. This documentation guides you through the main features of the system.

## 1. Knowledge Base Management

The first step is to create and manage your knowledge bases (collections).

### Creating a Knowledge Base

1. Navigate to the **Knowledge Base** tab in the RAG system interface
2. In the "Create a new knowledge base" section, enter a name for your collection
3. Click the **Create** button
4. Your new knowledge base will appear in the "Knowledge bases" list

### Deleting a Knowledge Base

1. In the "Delete a knowledge base" section, select the base to delete from the dropdown menu
2. Click the **Delete** button

## 2. Document Import

Once your knowledge base is created, you can add documents to it.

### Uploading Documents

1. Navigate to the **Upload** tab
2. Select the target knowledge base from the dropdown menu
3. Drag and drop your files into the designated area or click **Browse files** to select them
   - Supported formats: txt, pdf, md, csv, doc, docx, xls, xlsx, html, pptx, py
   - Limit: 200MB per file
4. Click **Import** to add the documents to your knowledge base

### Viewing Imported Documents

1. After importing your documents, you can view the list of available files
2. The system displays for each document:
   - Filename
   - File type
   - Embeddings status (✓ if generated)
   - File size
   - Import date

### Deleting a Document

1. In the "Delete Document" section, select the document to delete
2. Click the **Delete Document** button

## 3. Collection Metadata

The **Collection Metadata** tab provides detailed information about your knowledge base.

### Available Information

- **Total Chunks**: Total number of text segments created from your documents
- **Document Count**: Number of documents in the collection
- **Embedding Type**: Type of embedding used for indexing
- **Specific Model**: Specific embedding model (e.g., all-mpnet-base-v2)
- **Dimensions**: Dimensions of the embedding vectors (e.g., 768)
- **Chunk Size**: Size of text segments (in characters)
- **Chunk Overlap**: Overlap between segments (in characters)
- **Files on Disk**: Number of physical files stored

### Viewing Chunks

You can examine the chunks (segments) extracted from your documents:

1. Select a document from the "Select a document to view sample chunks" dropdown menu
2. View the content of each chunk by clicking on "Chunk 1", "Chunk 2", etc.
3. For each chunk, you can see:
   - The textual content
   - Associated technical metadata

## 4. Integration with Your Applications

To use your RAG knowledge base in your applications:

1. Configure your chatbot or application to use the desired collection
2. In your application settings, select the knowledge base (collection) to use
3. Your application will now be able to answer questions based on the information contained in your documents

## Best Practices

- Create separate knowledge bases for different domains or topics
- Use descriptive names for your collections (e.g., "product-documentation", "customer-FAQ")
- Verify that your documents are properly indexed (✓) before using them
- If possible, segment very large documents before importing them
- Regularly test your applications to verify the relevance of generated answers

