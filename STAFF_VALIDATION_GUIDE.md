# Guest Information Requirements - Quick Reference

## Required Fields

When creating or modifying a reservation, **ALL** of the following fields must be filled:

- ✓ Guest Name
- ✓ Phone Number
- ✓ Email Address

## Phone Number Format

### ✓ CORRECT Format
Phone numbers must contain **ONLY NUMBERS** (0-9)

**Examples:**
- `1234567890`
- `60123456789`
- `0123456789`

### ✗ INCORRECT Format
Do NOT include:
- Dashes: ~~`123-456-7890`~~
- Parentheses: ~~`(123) 456-7890`~~
- Spaces: ~~`123 456 7890`~~
- Letters: ~~`123abc456`~~

**Error Message**: 
> "Please enter a valid phone number containing only digits"

**How to Fix**: Remove all dashes, spaces, parentheses, and letters. Enter only the digits.

---

## Email Address Format

### ✓ CORRECT Format
Email addresses must end with:
- `@gmail.com` OR
- `@outlook.com`

**Examples:**
- `john.doe@gmail.com`
- `jane.smith@outlook.com`
- `contact123@gmail.com`
- `hotel.guest@outlook.com`

**Note**: Uppercase and lowercase are both accepted
- `USER@GMAIL.COM` ✓
- `Test@Outlook.com` ✓

### ✗ INCORRECT Format
The following email domains are NOT accepted:
- ~~`user@yahoo.com`~~
- ~~`test@hotmail.com`~~
- ~~`contact@company.com`~~
- ~~`person@email.net`~~

**Error Message**: 
> "Email must end with @gmail.com or @outlook.com"

**How to Fix**: Ask the guest for their Gmail or Outlook email address.

---

## Common Error Messages

| Error Message | What It Means | How to Fix |
|--------------|---------------|------------|
| "Guest name is required" | Name field is empty | Fill in the guest's name |
| "Phone number is required" | Phone field is empty | Fill in the phone number |
| "Email address is required" | Email field is empty | Fill in the email address |
| "Please enter a valid phone number containing only digits" | Phone has dashes, spaces, or letters | Remove formatting, keep only numbers |
| "Email must end with @gmail.com or @outlook.com" | Email domain is not allowed | Use Gmail or Outlook email |

---

## Step-by-Step: Creating a Valid Reservation

1. **Fill in Guest Name**
   - Enter the guest's full name
   - Example: `John Doe`

2. **Fill in Phone Number**
   - Enter ONLY numbers (no dashes, spaces, or parentheses)
   - Example: `1234567890`

3. **Fill in Email Address**
   - Make sure it ends with `@gmail.com` or `@outlook.com`
   - Example: `john.doe@gmail.com`

4. **Select Dates**
   - Choose check-in and check-out dates

5. **Select Number of Guests**
   - Enter the number of guests

6. **Check Availability**
   - Click "Check Availability" to see available rooms

7. **Select Room**
   - Choose a room from the dropdown

8. **Create Reservation**
   - Click "Create Reservation"
   - If all information is valid → Reservation created! ✓
   - If there's an error → Read the error message and fix the issue

---

## Quick Tips

💡 **Before clicking "Create Reservation"**, double-check:
1. Guest name is filled in
2. Phone number has only digits (no dashes or spaces)
3. Email ends with @gmail.com or @outlook.com

💡 **If you get an error**:
1. Read the error message carefully
2. Fix the issue mentioned in the message
3. Try creating the reservation again

💡 **Phone number example transformations**:
- Guest writes: `(012) 345-6789`
- You enter: `0123456789` ✓

💡 **Email example**:
- Guest says: "My email is john at yahoo dot com"
- Response: "Do you have a Gmail or Outlook email instead?"
- Guest provides: `john.doe@gmail.com` ✓

---

## Need Help?

If you encounter any issues or have questions about the validation requirements, please contact the IT support team or refer to the full documentation in `VALIDATION_IMPLEMENTATION.md`.
