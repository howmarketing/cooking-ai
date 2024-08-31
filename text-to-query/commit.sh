#!/bin/bash

git add -A

git commit -m "playground notebook updated with new code examples and experiments

- [x] Add frequency dictionary and Counter examples
- [x] Implement bigram analysis using defaultdict
- [x] Explore word prediction and most common words
- [x] Add environment variable handling with dotenv
- [x] Include various text processing and data structure experiments"

git status

# Ask user if he wants to push the changes to the remote repository
read -p "Do you want to push the changes to the remote repository? (y/n): " push

if [ "$push" = "y" ]; then
    git push
else
    echo "Changes not pushed to the remote repository."
fi