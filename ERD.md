AUTHORS

id PK
name
bio
--------------|
--------------| many-to-many
--------------|

BOOK_AUTHORS

book_id PK, FK
author_id PK, FK
--------------| association
--------------|

BOOKS

id PK
title
isbn UNIQUE
year_published
available_copies
--------------|
--------------| one book can have many checkout records
--------------|

CHECKOUTS

id PK
book_id FK
member_id FK
checkout_date
due_date
return_date
--------------|
--------------| many checkouts can belong to one member
--------------|

MEMBERS

id PK
name
email UNIQUE
membership_date
phone
