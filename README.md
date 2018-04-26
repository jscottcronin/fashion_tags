# fashion_tags
A competition to build fashion image tagging models.

## Automating connection to paperspace box via ssh
With the paperspace box running (turn on at [paperspace.com](https://www.paperspace.com/)), please follow the instructions below:

First we need to install ssh-copy-id via brew:
```bash
brew install ssh-copy-id
```
Next, we need to store connection criteria into our id_rsa file
```bash
ssh-copy-id -i ~/.ssh/id_rsa.pub paperspace@OUR_IP_ADDRESS
```
Finally, on your local machine, open `~/.ssh/config` and add the following lines:
```
Host picture_perfect
  Hostname OUR_IP_ADDRESS
  IdentityFile ~/.ssh/id_rsa
  User paperspace
  LocalForward 8888 localhost:8888
```
you can now log into the paperspace box by using:
```bash
ssh picture_perfect
```
