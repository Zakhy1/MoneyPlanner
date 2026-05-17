# User

* email - varchar(128)
* status - enum(default, premium)
* password - varchar(255)
* is_active - bool
* created_at - timestamp with timezone

[//]: # (# Group)

[//]: # ()
[//]: # (* name - varchar&#40;64&#41;)

[//]: # (* is_active - bool)

[//]: # (* members - list&#40;User&#41;)

[//]: # (* owner - User)

[//]: # ()
[//]: # (# UserGroup)

[//]: # ()
[//]: # (* user - User)

[//]: # (* group - Group)
