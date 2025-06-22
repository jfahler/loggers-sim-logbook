# Player Profiles Management

The `profiles.json` file is used to maintain a whitelist of known real players to prevent them from being incorrectly filtered as AI units.

## File Structure

```json
{
  "players": [
    {
      "callsign": "six",
      "aliases": ["(HHC/229) Six"],
      "notes": "Squadron leader"
    },
    {
      "callsign": "machinegun817",
      "aliases": ["Gunner 1 | Machinegun817"],
      "notes": "Gunner callsign"
    }
  ]
}
```

## Fields

- **callsign**: The primary callsign/nickname for this player (used for AI filtering)
- **aliases**: Array of alternative names/aliases this player uses in-game
- **notes**: Optional notes about the player (squadron, role, etc.)

## How It Works

1. When processing XML files, the system extracts pilot names
2. Each pilot name is checked against the callsigns and aliases in this file
3. If there's a match, the pilot is marked as a real player
4. If no match is found, the AI filter applies pattern matching rules
5. This prevents false positives where real players are incorrectly filtered as AI

## Adding New Players

To add a new player, copy the template structure and fill in the details:

```json
{
  "callsign": "new_player_callsign",
  "aliases": ["New Player | Callsign", "Another Alias"],
  "notes": "Brief description or notes about this player"
}
```

## AI Filtering Process

The AI filter uses a multi-layered approach:

1. **Whitelist Check**: First checks if the pilot is in `profiles.json`
2. **Group Analysis**: Checks if the group contains AI indicators (IQ, AI, bot, etc.)
3. **Pattern Matching**: Applies regex patterns to identify AI naming conventions
4. **Military Unit Detection**: Identifies military units, ships, ground vehicles
5. **Player Pattern Recognition**: Looks for common player naming patterns

## Benefits

- **Prevents False Positives**: Known players are never filtered out as AI
- **Flexible**: Supports multiple aliases per player
- **Admin Controlled**: Easy to manage without code changes
- **Documentation**: Notes field helps track player information

## Maintenance

- Add new players as they join your server
- Update aliases when players change their names
- Remove players who are no longer active
- Use the notes field to track squadron assignments or roles

## Example Use Cases

- **New Player Joins**: Add their callsign and any aliases they use
- **Player Changes Name**: Add the new name as an alias
- **Squadron Assignment**: Update notes to reflect current role
- **Inactive Player**: Remove from the list to clean up

## Troubleshooting

If a real player is being filtered as AI:

1. Check if they're in `profiles.json`
2. Add their callsign and aliases if missing
3. Verify the spelling matches exactly (case-insensitive)
4. Test with the AI filter to confirm they're now recognized

If an AI unit is getting through:

1. Check the AI filter patterns in `xml_parser.py`
2. Add new patterns if needed
3. Update the group analysis rules 