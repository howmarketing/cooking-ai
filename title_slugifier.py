from slugify import slugify

def slugifyTitle(title):
    return slugify(title, allow_unicode=True)

if __name__ == '__main__':
    title = "Terraform | Deploy a docker container with a node app locally with Terraform"
    slug = slugifyTitle(title)
    print(slug)