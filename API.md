# API reference

This table lists all available API endpoints.

| Name                 | API Path                  | Request Type | Body (optional)                | Token Required | Role  |
|----------------------|---------------------------|--------------|--------------------------------|----------------|-------|
| Signup               | /api/signup               | POST         | -                              | Yes            | User  |
| Get profile          | /api/profile              | GET          | -                              | Yes            | User  |
| Update profile pic   | /api/profile/picture      | PUT          | {"profile_pic_url": <new_url>} | Yes            | User  |
| Get books            | /api/books                | GET          | -                              | No             | -     |
| Get book by id       | /api/books/{book_id}      | GET          | -                              | No             | -     |
| Admin add book       | /api/admin/book           | POST         | JSON book object               | Yes            | Admin |
| Admin delete book    | /api/admin/book/{book_id} | DELETE       | -                              | Yes            | Admin |
| Get wishlist         | /api/wishlist             | GET          | -                              | Yes            | User  |
| Add to wishlist      | /api/wishlist/            | POST         | {'book_id': <book_id>}         | Yes            | User  |
| Delete from wishlist | /api/wishlist/{book_id}   | DELETE       | -                              | Yes            | User  ||                           |              |                                |                |       |

**Notes:**

* The body format is JSON.