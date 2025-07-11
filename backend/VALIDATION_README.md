# Input Validation System

This document describes the comprehensive input validation system implemented for the Loggers DCS Squadron Logbook application.

## Overview

The validation system provides security, data integrity, and input sanitization for all user inputs and file uploads. It prevents common attack vectors like:

- **Path Traversal**: Using `secure_filename()` and path validation
- **Script Injection**: Regex pattern validation for dangerous characters
- **Buffer Overflow**: Length limits on all string inputs
- **XML External Entity (XXE)**: XML content validation
- **Denial of Service**: File size limits and event count validation

## Validation Modules

### 1. File Upload Validation (`validate_file_upload`)

Validates uploaded files for security and format requirements.

**Checks:**
- File existence and readability
- Filename length (max 255 characters)
- File extension (only `.xml` allowed)
- File size (max 50MB)
- Filename character validation

**Usage:**
```python
from validation import validate_file_upload

is_valid, error = validate_file_upload(file_object)
if not is_valid:
    return jsonify({"error": error}), 400
```

### 2. XML Content Validation (`validate_xml_content`)

Validates XML file structure and content for security.

**Checks:**
- File existence and readability
- Valid XML format
- Root element must be "Tacview"
- Required "Events" section
- Event count limit (max 100,000 events)
- Event structure validation

**Usage:**
```python
from validation import validate_xml_content

is_valid, error = validate_xml_content(file_path)
if not is_valid:
    return jsonify({"error": error}), 400
```

### 3. String Field Validation

#### Pilot Name Validation (`validate_pilot_name`)
- **Length**: 1-100 characters
- **Pattern**: `^[a-zA-Z0-9\s\-_|\.]+$`
- **Allowed**: Letters, numbers, spaces, hyphens, underscores, pipes, dots

#### Callsign Validation (`validate_callsign`)
- **Length**: 1-50 characters
- **Pattern**: `^[a-zA-Z0-9\s\-_|\.]+$`
- **Allowed**: Letters, numbers, spaces, hyphens, underscores, pipes, dots

#### Mission Name Validation (`validate_mission_name`)
- **Length**: 1-200 characters
- **Pattern**: `^[a-zA-Z0-9\s\-_\.]+$`
- **Allowed**: Letters, numbers, spaces, hyphens, underscores, dots

#### Aircraft Name Validation (`validate_aircraft_name`)
- **Length**: 1-100 characters
- **Pattern**: `^[a-zA-Z0-9\s\-_\.\/]+$`
- **Allowed**: Letters, numbers, spaces, hyphens, underscores, dots, forward slashes
- **Whitelist**: Validates against known aircraft types

### 4. Platform Validation (`validate_platform`)

Validates platform names against allowed values.

**Allowed Platforms:**
- `DCS` - Digital Combat Simulator
- `BMS` - BMS Falcon
- `IL2` - IL-2 Sturmovik

### 5. Numeric Validation (`validate_numeric_value`)

Validates numeric values with optional min/max bounds.

**Usage:**
```python
from validation import validate_numeric_value

# Validate with bounds
is_valid, error = validate_numeric_value(value, "field_name", min_val=0, max_val=100)

# Validate without bounds
is_valid, error = validate_numeric_value(value, "field_name")
```

### 6. List Validation (`validate_callsigns_list`)

Validates lists of callsigns.

**Checks:**
- Must be a list
- Max 100 callsigns
- Each callsign must pass individual validation

### 7. Data Structure Validation

#### Pilot Data Validation (`validate_pilot_data`)
Validates complete pilot mission data structures.

**Required Fields:**
- `date`: Mission date
- `mission`: Mission name
- `aircraft`: Aircraft type
- `platform`: Platform name

**Optional Numeric Fields:**
- `aa_kills`, `ag_kills`, `frat_kills`: 0-10,000
- `rtb`, `ejections`, `deaths`: 0-10,000
- `flight_minutes`: 0-10,000

#### Discord Data Validation (`validate_discord_data`)
Validates Discord webhook data structures.

**Required Fields:**
- `pilotName`: Pilot name

**Optional Fields:**
- `pilotCallsign`, `aircraftType`, `missionName`: String validation
- `totalFlights`, `totalFlightTime`, etc.: 0-100,000

### 8. String Sanitization (`sanitize_string`)

Removes dangerous characters and limits string length.

**Removes:**
- Null bytes (`\x00`)
- Control characters (`\x00-\x08`, `\x0B`, `\x0C`, `\x0E-\x1F`, `\x7F`)
- Newlines (`\n`, `\r`)

**Usage:**
```python
from validation import sanitize_string

clean_string = sanitize_string(dirty_string, max_length=1000)
```

## Configuration Constants

```python
# File limits
MAX_FILENAME_LENGTH = 255
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_CALLSIGNS_COUNT = 100

# String limits
MAX_PILOT_NAME_LENGTH = 100
MAX_CALLSIGN_LENGTH = 50
MAX_MISSION_NAME_LENGTH = 200
MAX_AIRCRAFT_NAME_LENGTH = 100
MAX_NOTE_LENGTH = 1000

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.xml'}

# Valid platforms
VALID_PLATFORMS = {'DCS', 'BMS', 'IL2'}
```

## Integration Examples

### File Upload Endpoint
```python
@app.route('/upload_xml', methods=['POST'])
def upload_xml():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    
    # Validate file upload
    is_valid, error = validate_file_upload(file)
    if not is_valid:
        return jsonify({"error": error}), 400

    # Save file
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Validate XML content
    is_valid, error = validate_xml_content(filepath)
    if not is_valid:
        os.remove(filepath)  # Clean up
        return jsonify({"error": error}), 400

    # Process file...
```

### Discord Webhook Endpoint
```python
@app.route('/discord/pilot-stats', methods=['POST'])
def post_pilot_stats():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
        
    data = request.get_json()
    
    # Validate Discord data
    is_valid, error = validate_discord_data(data)
    if not is_valid:
        return jsonify({"error": error}), 400
        
    # Process data...
```

### Squadron Callsigns Update
```python
@app.route('/squadron-callsigns', methods=['POST'])
def update_squadron_callsigns():
    data = request.get_json()
    callsigns = data.get('callsigns', [])
    
    # Validate callsigns list
    is_valid, error = validate_callsigns_list(callsigns)
    if not is_valid:
        return jsonify({"error": error}), 400
    
    # Sanitize callsigns
    valid_callsigns = [sanitize_string(callsign.strip()) for callsign in callsigns if callsign.strip()]
    
    # Save callsigns...
```

## Error Handling

All validation functions return a tuple: `(is_valid: bool, error_message: str)`

**Example:**
```python
is_valid, error = validate_pilot_name(pilot_name)
if not is_valid:
    logger.warning(f"Invalid pilot name: {error}")
    return jsonify({"error": error}), 400
```

## Testing

Run the validation test suite:

```bash
cd backend
python test_validation.py
```

The test suite covers:
- All validation functions
- Edge cases and error conditions
- String sanitization
- XML content validation
- Data structure validation

## Security Considerations

1. **Input Validation**: All user inputs are validated before processing
2. **Output Sanitization**: Data is sanitized before storage
3. **File Upload Security**: Files are validated for type, size, and content
4. **XML Security**: XML content is validated to prevent XXE attacks
5. **Length Limits**: All strings have reasonable length limits
6. **Character Whitelisting**: Only safe characters are allowed in inputs

## Best Practices

1. **Always validate inputs** before processing
2. **Sanitize data** before storage
3. **Use specific validation** for different data types
4. **Log validation failures** for monitoring
5. **Clean up files** on validation errors
6. **Return user-friendly error messages**
7. **Test validation functions** regularly

## Maintenance

- Update `VALID_AIRCRAFT_TYPES` when new aircraft are added
- Adjust length limits based on application needs
- Monitor validation failure logs
- Update test cases when validation rules change
- Review security implications of any changes 