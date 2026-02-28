# Item Management Form – Fix for `deleteError is not defined` and 404s

## 1. Fix `deleteError is not defined`

The error happens because `deleteError` is used (e.g. in JSX) but never declared.

**In your `ItemManagementForm` component (in App.jsx or wherever it lives):**

### Add state for delete error

With your other `useState` calls, add:

```js
const [deleteError, setDeleteError] = useState(null);
```

### When you delete a medicine

- **On success:** clear the error and update list (e.g. remove the item from state).
- **On failure:** set the error message.

Example:

```js
const handleDelete = async (id) => {
  setDeleteError(null);
  try {
    const res = await fetch(`http://127.0.0.1:8000/api/medicines/${id}/`, { method: 'DELETE' });
    if (!res.ok) {
      if (res.status === 404) {
        // Already deleted – remove from local list
        setItems(prev => prev.filter(item => item.id !== id));
        return;
      }
      throw new Error('Delete failed');
    }
    setItems(prev => prev.filter(item => item.id !== id));
  } catch (err) {
    setDeleteError(err?.message || 'Failed to delete item');
  }
};
```

### Show the error in the UI

Where you want to show the delete error (e.g. above the table or in a modal):

```jsx
{deleteError && (
  <div className="error-message" role="alert">
    {deleteError}
  </div>
)}
```

Optional: clear `deleteError` when the user closes the message or when they start another action.

---

## 2. Fix 404 on `/api/medicines/5/` and `/api/medicines/4/`

404 means that medicine **id 4 and 5 do not exist** in the database (e.g. deleted or DB reset). The API is behaving correctly.

**What to do in the frontend:**

1. **List from one endpoint**  
   Load the list from `GET http://127.0.0.1:8000/api/medicines/` and use that response as the source of truth. Do not keep hardcoded or stale IDs (like 4 and 5) in state.

2. **When fetching a single medicine (e.g. for edit)**  
   If `GET /api/medicines/{id}/` returns 404:
   - Remove that `id` from your local list (or mark as “not found”), and
   - Do not render a row or form that still expects that id to exist.

   Example:

   ```js
   const loadMedicine = async (id) => {
     const res = await fetch(`http://127.0.0.1:8000/api/medicines/${id}/`);
     if (res.status === 404) {
       setItems(prev => prev.filter(item => item.id !== id));
       return;
     }
     const data = await res.json();
     setSelectedItem(data);
   };
   ```

3. **When loading the list**  
   Use only the IDs returned by `GET /api/medicines/`. If the list is empty, show an empty state instead of calling detail endpoints for old IDs.

---

## 3. Summary

| Issue | Cause | Fix |
|-------|--------|-----|
| `deleteError is not defined` | Variable used but not declared | Add `const [deleteError, setDeleteError] = useState(null);` and set/clear it in delete handler and show it in JSX. |
| 404 on `/api/medicines/4/`, `/api/medicines/5/` | Those IDs no longer exist in DB | Use only IDs from `GET /api/medicines/` and handle 404 by removing the id from local state. |

Apply these changes in your React app (e.g. in `App.jsx` where `ItemManagementForm` is defined). If you can open the frontend project in this workspace, the exact line numbers can be adjusted to match your file.
