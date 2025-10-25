Working principles of two way sync:

- filters allows you to walk through files to sync in one remote storage.
- for each of files that should be included on the left,
    - we find their counterpart on the right, if they exist
    - we run the comparaison between the two and the database,
    - and take immediate actions
- then we filter on the other remote storage
- exclude files that were just seen (it avoids useless remote actions that have already been executed previously, at the expense of potentially missing updates that happened between syncing on the first round and now)
