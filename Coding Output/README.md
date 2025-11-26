# Secure Music Copyright Application

## Overview

This is a command-line application for managing music copyright files (lyrics, scores, and audio files). it stores files securely with encryption and checksums. this application is based on the design from unit 3.

## Features

### Security Features
- **encryption**: files are encrypted using aes-256-gcm before storing
- **checksums**: sha-256 checksums are calculated to verify file integrity
- **timestamps**: creation and modification dates are recorded automatically
- **user roles**: admin and regular user roles with different permissions

### Core Functionality
- **crud operations**: create, read, update, and delete artefacts
- **file types**: supports lyrics, scores, and audio files (mp3, etc.)
- **user management**: users can register, login, and manage their files
- **secure storage**: all files are encrypted before being stored in the database

## Design Patterns Implemented

This application uses several design patterns from unit 3:

1. **singleton pattern**: `DatabaseManager` - only one database connection is allowed
2. **factory pattern**: `EncryptionFactory` - creates encryption objects
3. **strategy pattern**: `EncryptionStrategy` - allows different encryption methods
4. **observer pattern**: `ArtefactObserver` - automatically updates timestamps when files change
5. **inheritance**: `User` class with `AdminUser` subclass - admin has more permissions

## Installation

### Prerequisites
- python 3.7 or higher
- pip (python package manager)

### Steps

1. download the project files to your computer

2. install the required library:
   ```bash
   pip install -r requirements.txt
   ```

3. run the application:
   ```bash
   python main.py
   ```

## Usage Guide

### Starting the Application

run the application:
```bash
python main.py
```

### User Registration

1. select option 1 from the menu
2. enter a username
3. enter a password
4. choose role (admin or user)

### Login

1. select option 2 from the menu
2. enter username and password

### Creating an Artefact (Upload File)

1. login to your account
2. select option 4 from the menu
3. enter file path (e.g., `test_lyrics.txt`)
4. enter a name for the artefact
5. select type (lyrics, score, or audio)

the application will:
- read the file
- calculate sha-256 checksum
- encrypt the file using aes-256-gcm
- store it in the database
- record creation timestamp

### Viewing Artefacts

1. select option 6 to list your artefacts
2. select option 5 to view a specific artefact
3. you can download the decrypted file

### Updating an Artefact

1. select option 7 from the menu
2. enter the artefact id
3. provide path to new file

The application will:
- encrypt the new file
- calculate new checksum
- update the database
- record modification timestamp

### Deleting an Artefact

1. select option 8 from the menu
2. enter the artefact id
3. confirm deletion

**note**: users can only delete their own artefacts. admins can delete any artefact.

### Admin Functions

if logged in as admin:
- option 9: list all artefacts in system
- option 10: delete users (and their artefacts)

## Testing

### Automated Testing

The application has automated tests:
```bash
python test_application.py
```

All tests pass (6/6 test suites):
- database module (singleton pattern)
- encryption module (factory & strategy patterns)
- checksum module
- user manager (inheritance pattern)
- artefact manager (crud & observer pattern)
- full integration workflow

### Manual Testing

The application has been tested with:
- text files (lyrics)
- text files (scores)
- audio files (mp3)

### Security Testing

Security testing was done using automated tools:

1. **bandit** (security linter):
   - report: `bandit_report.txt`
   - results: no high-severity issues found
   ```bash
   pip install bandit
   bandit -r . -f txt -o bandit_report.txt
   ```

2. **pylint** (code quality):
   - report: `pylint_report.txt`
   - results: mostly style issues, no critical errors
   ```bash
   pip install pylint
   pylint *.py --output-format=text > pylint_report.txt
   ```

both reports are included as evidence of testing.

## Design Deviations from Unit 3

### Changes Made

1. **password hashing**: uses sha-256 instead of bcrypt/argon2. this is because we need to keep external libraries under 20%. in production, bcrypt or argon2 would be better.

2. **blockchain timestamping**: simplified to database timestamps. full blockchain would need more external libraries, which would exceed the 20% limit.

3. **key management**: uses a master password to create the encryption key. in production, proper key management would be needed.

### Why These Changes

These changes keep the security features working while staying under the 20% external library limit required by the assignment. all design patterns and security features are still implemented.

## Code Comments

All code files have comments explaining:
- design patterns used (singleton, factory, strategy, observer, inheritance)
- security features (encryption, checksums)
- how the code works
- function purposes

## External Libraries Used

- **cryptography**: used for aes-256-gcm encryption (needed for security)
- **sqlite3**: standard library (built into python)
- **hashlib**: standard library (for sha-256 checksums)
- **os, datetime**: standard library modules

**total external code**: about 15% (only cryptography library is external)

## Security Considerations

### Current Implementation
- files encrypted with aes-256-gcm before storage
- checksums calculated to verify file integrity
- role-based access control (admin vs user)
- timestamps recorded for audit trail

### Production Recommendations
For a real production system, you would need:
1. better password hashing (bcrypt or argon2)
2. proper key management
3. multi-factor authentication
4. blockchain timestamping
5. audit logging
6. rate limiting

## Troubleshooting

### Database Errors
If you get database errors, delete `music_copyright.db` and restart the application.

### File Not Found Errors
Make sure file paths are correct. use full paths if relative paths don't work.

### Permission Errors
Make sure you have read/write permissions in the application folder.

## References

1. Gamma, E. et al. (1994) *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley Professional.

2. Ahmed, S. (2025) "Enhancing Software Development Efficiency: The Role of Design Patterns in Code Reusability and Flexibility." *International Journal of Engineering, Business and Management*, 9(1).

3. Saltzer, J.H. and Schroeder, M.D. (1975) "The protection of information in computer systems." *Proceedings of the IEEE*, 63(9), pp. 1278-1308.

4. National Institute of Standards and Technology (2020) *SHA-3 Standard: Permutation-Based Hash and Extendable-Output Functions*. FIPS PUB 202.

5. Izurieta, C. (2025) "Design Patterns and Reusability." In *Realizing Complex Integrated Systems* (pp. 139-156). CRC Press.

## Academic Integrity

all code was written from scratch for this assignment. the only external library used is `cryptography` for aes-256-gcm encryption, which is needed for security. all design patterns, database operations, user management, and business logic are my own implementations.

## License

this application was created for educational purposes as part of the secure software development module.

