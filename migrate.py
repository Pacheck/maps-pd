from services import bigquery


def main():
  bigquery.run_migrations()


if __name__ == "__main__":
  main()
