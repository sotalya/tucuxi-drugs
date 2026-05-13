# tucuxi-drugs

This repository is part of the [Tucuxi](https://www.tucuxi.ch) project. It contains the drug model files (population pharmacokinetic models) used by Tucuxi for model-informed precision dosing (MIPD).

## Drug files

Drug files use the `.tdd` format (XML, validated against `drugfiles/drugfile.xsd`).

The naming convention is:

```
ch.tucuxi.<drugname>.<firstauthor><year>.tdd
```

For specific sub-models (for instance with different targets):

```
ch.tucuxi.<drugname>.<firstauthor><year>-<something>.tdd
```


### Available models

| Drug | Models |
|------|--------|
| Imatinib | Gotta 2012 |

## Repository structure

```
.
├── drugfiles/                     drug files (*.tdd) and XSD schema (drugfile.xsd)
├── scripts/                       helper scripts (build light/ultralight drug file bundles)
├── validation/
│   └── comparative/               comparative validation (Python, against reference software)
└── dev/                           work-in-progress drug files
```

## Validation

### Automated tests

From `validation/tests/scripts/`, run:

```bash
./check_all.sh
```

This validates all drug files against the schema and runs the drug file checker.

### Comparative validation

The `validation/comparative/` directory contains Python scripts to compare Tucuxi predictions against reference data:

```bash
cd validation/comparative
pip install -r requirements.txt
python tucuvalidation.py
```

## Scripts

The `scripts/` directory provides tools to generate lightweight drug file bundles (useful for embedded or bandwidth-constrained deployments):

```bash
cd scripts
./generatealllight.sh      # generates light and ultra-light bundles in drugfileslight/
```

