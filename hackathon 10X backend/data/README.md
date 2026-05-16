# Backend Data Folder

Put the private Excel input files for local runs in this folder, then set:

```env
EXCEL_DATA_FOLDER=./data
```

The backend currently looks for a `Paid Clients` Excel file such as:

```text
Paid Clients 20260515.xlsb
```

and reads the `Client Base` sheet from it.

These files are intentionally ignored by Git because they may contain private seller data and can be large. Share them separately through an approved secure drive, or provide a redacted sample file with the same sheet and column structure if teammates only need to test the app.
