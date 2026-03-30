# ERP Naming Convention Guide (Exact Forms)

This document defines the **exact naming format** for every item in the ERP project.

The goal is simple:

> If two developers create the same type of item, they must naturally give it the same naming style.

This is not a suggestion.
This is the official naming contract of the project.

---

# 1) General Naming Rules

## 1.1 Language
All names in code must be in **French or English only**.

---

## 1.2 Naming styles by item type

| Item Type | Naming Style |
|----------|--------------|
| Class | `PascalCase` |
| File | `snake_case` |
| Folder | `snake_case` |
| Function | `snake_case` |
| Variable | `snake_case` |
| Constant | `UPPER_CASE` |
| Widget objectName | `snake_case` |

---

# 2) Exact Naming Forms

---

# 3) Window Folder

## Exact form

```text id="nlgnli"
<window_name>/
```

## Examples

✅ Good:

* `login/`
* `dashboard/`
* `article/`
* `fournisseur/`
* `invoice/`

❌ Bad:

* `Login/`
* `login_window/`
* `dashboard_page/`

## Rule

The folder name must be the **feature name only**.

---

# 4) Window UI File

## Exact form

```text id="31vf2d"
<window_name>.ui
```

## Examples

✅ Good:

* `login.ui`
* `dashboard.ui`
* `article.ui`

❌ Bad:

* `login_window.ui`
* `ui_login.ui`
* `dashboard_page.ui`

## Rule

The `.ui` file represents the visual layout only.

---

# 5) Window Main Python File

This is the file that:

* loads the `.ui`
* initializes the window
* connects signals
* calls helper functions

## Exact form

```text id="6xmbc6"
<window_name>.py
```

## Examples

✅ Good:

* `login.py`
* `dashboard.py`
* `article.py`

❌ Bad:

* `login_window.py`
* `window_login.py`
* `dashboard_main.py`

---

# 6) Window Helper Functions File

This file contains the functions used by that window.

## Exact form

```text id="3xh1g5"
<window_name>_funcs.py
```

## Examples

✅ Good:

* `login_funcs.py`
* `dashboard_funcs.py`
* `article_funcs.py`

❌ Bad:

* `functions.py`
* `helpers.py`
* `utils.py`

---

# 7) Window Class

## Exact form

```text id="zn9h4k"
<WindowName>Window
```

## Examples

✅ Good:

* `LoginWindow`
* `DashboardWindow`
* `NouveauArticleWindow`
* `FournisseurWindow`

❌ Bad:

* `Login`
* `WindowLogin`
* `LoginPage`
* `Ui_Login`

## Rule

Every real window class must end with:

```text id="tq83nd"
Window
```

---

# 8) Custom Widget Folder (Optional)

If a custom widget has its own files/folder:

## Exact form

```text id="p7f4m6"
<widget_name>/
```

## Examples

✅ Good:

* `article_card/`
* `user_badge/`
* `invoice_row/`

---

# 9) Custom Widget UI File

If a custom widget has a `.ui` file:

## Exact form

```text id="oj20jv"
<widget_name>.ui
```

## Examples

✅ Good:

* `article_card.ui`
* `user_badge.ui`

---

# 10) Custom Widget Main Python File

## Exact form

```text id="h3tw9x"
<widget_name>_widget.py
```

## Examples

✅ Good:

* `article_card_widget.py`
* `user_badge_widget.py`
* `invoice_row_widget.py`

❌ Bad:

* `widget_article.py`
* `card.py`
* `custom_widget.py`

---

# 11) Custom Widget Class

## Exact form

```text id="uv1uxv"
<WidgetName>Widget
```

## Examples

✅ Good:

* `ArticleCardWidget`
* `UserBadgeWidget`
* `InvoiceRowWidget`
* `StatsCardWidget`

❌ Bad:

* `CardWidget`
* `MyWidget`
* `CustomWidget`

## Rule

Every custom widget class must end with:

```text id="c6z2fh"
Widget
```

---

# 12) Function Naming (Exact Forms)

A function name must always start with a **verb**.

---

## 12.1 General action function

## Exact form

```text id="nfxk4d"
<verb>_<object>()
```

## Examples

✅ Good:

* `save_article()`
* `delete_user()`
* `load_clients()`
* `clear_form()`

❌ Bad:

* `article_save()`
* `user_delete()`
* `form_clear()`

---

## 12.2 Validation function

## Exact form

```text id="ef4x66"
validate_<thing>()
```

## Examples

✅ Good:

* `validate_password()`
* `validate_email()`
* `validate_article_form()`

---

## 12.3 Authentication / checking function

## Exact form

```text id="c7pbmv"
check_<thing>()
authenticate_<thing>()
```

## Examples

✅ Good:

* `check_user()`
* `authenticate_user()`
* `check_permissions()`

> Use `check_...` only if the function is mainly for verification.

---

## 12.4 Insert / create function

## Exact form

```text id="dnpw4y"
add_<thing>()
create_<thing>()
```

## Examples

✅ Good:

* `add_user()`
* `add_article()`
* `create_invoice()`

---

## 12.5 Update function

## Exact form

```text id="k4c3cc"
update_<thing>()
```

## Examples

✅ Good:

* `update_stock()`
* `update_user_role()`
* `update_invoice_status()`

---

## 12.6 Delete function

## Exact form

```text id="f5jdu8"
delete_<thing>()
remove_<thing>()
```

## Examples

✅ Good:

* `delete_article()`
* `remove_supplier()`

---

## 12.7 Fetch / read database function

## Exact form

```text id="j7zw7s"
fetch_<thing>()
get_<thing>()
find_<thing>()
```

## Examples

✅ Good:

* `fetch_one()`
* `fetch_all()`
* `get_user_role()`
* `find_article_by_code()`

---

## 12.8 Calculation function

## Exact form

```text id="l1t8ew"
calculate_<thing>()
```

## Examples

✅ Good:

* `calculate_ttc()`
* `calculate_total_ht()`
* `calculate_balance()`

---

## 12.9 UI event handler function

For functions connected directly to signals:

## Exact form

```text id="k7dm0o"
on_<widget_name>_<event>()
```

## Examples

✅ Good:

* `on_login_button_clicked()`
* `on_search_input_changed()`
* `on_save_button_clicked()`
* `on_status_combobox_changed()`

❌ Bad:

* `login_clicked()`
* `button_pressed()`
* `save_function()`

## Rule

This is the official naming for **signal-connected functions**.

---

# 13) Variable Naming (Exact Forms)

---

## 13.1 Normal variable

## Exact form

```text id="1ggq5m"
<meaning>
```

## Examples

✅ Good:

* `username`
* `password`
* `user_role`
* `article_name`
* `total_price`

❌ Bad:

* `x`
* `value`
* `data1`
* `tmp`

---

## 13.2 Boolean variable

## Exact form

```text id="x0jwot"
is_<state>
has_<thing>
can_<action>
```

## Examples

✅ Good:

* `is_valid`
* `is_active`
* `has_stock`
* `can_edit`

❌ Bad:

* `valid`
* `stock_ok`
* `edit_permission`

---

## 13.3 List / collection variable

## Exact form

```text id="6u7zhq"
<plural_name>
```

## Examples

✅ Good:

* `users`
* `articles`
* `suppliers`
* `invoice_items`

---

## 13.4 Dictionary / grouped data variable

## Exact form

```text id="kw4s7d"
<thing>_data
```

## Examples

✅ Good:

* `user_data`
* `article_data`
* `document_data`

---

# 14) Constant Naming (Exact Form)

## Exact form

```text id="d68g8w"
UPPER_CASE
```

## Examples

✅ Good:

* `BASE_DIR`
* `WINDOWS_DIR`
* `ASSETS_DIR`
* `USER_ROLE`

❌ Bad:

* `BaseDir`
* `windowsDir`

---

# 15) Database Naming in Python Code

---

## 15.1 ID variable

## Exact form

```text id="r5g7wf"
<entity>_id
```

## Examples

✅ Good:

* `user_id`
* `article_id`
* `supplier_id`
* `document_id`

---

## 15.2 Foreign key variable

## Exact form

```text id="m59j1j"
<referenced_entity>_id
```

## Examples

✅ Good:

* `family_id`
* `client_id`
* `seller_id`

---

# 16) Widget Object Naming (Exact Forms)

This is mandatory for all Qt Designer widgets.

## Global exact form

```text id="8zv84r"
<purpose>_<type>
```

Example:

* `login_button`
* `password_input`
* `error_label`

The widget name must always answer:

1. What is its purpose?
2. What widget type is it?

---

# 17) Exact Widget Naming by Type

---

# 18) QPushButton

## Exact form

```text id="5tt7pq"
<action>_btn
```

## Examples

✅ Good:

* `login_btn`
* `save_btn`
* `cancel_btn`
* `add_article_btn`
* `delete_user_btn`
* `search_btn`

❌ Bad:

* `pushButton`
* `button1`
* `blue_button`

---

# 19) QLabel

## Exact form

```text id="ofv0dh"
<displayed_meaning>_lbl
```

## Examples

✅ Good:

* `username_lbl`
* `password_lbl`
* `error_lbl`
* `total_price_lbl`
* `welcome_lbl`

❌ Bad:

* `label1`
* `text_label`

---

# 20) QLineEdit

## Exact form

```text id="v0klws"
<input_meaning>_entry
```

## Examples

✅ Good:

* `username_entry`
* `password_entry`
* `search_entry`
* `barcode_entry`
* `article_name_entry`

❌ Bad:

* `lineEdit`
* `username_lineedit`
* `edit_username`

## Official rule

For `QLineEdit`, always use:

```text id="34h2g2"
_entry
```

not `_lineedit`

---

# 21) QTextEdit

## Exact form

```text id="o4ksm4"
<content_meaning>_txtedit
```

## Examples

✅ Good:

* `description_txtedit`
* `comment_txtedit`
* `notes_txtedit`

---

# 22) QPlainTextEdit

## Exact form

```text id="dzd8i8"
<content_meaning>_plaintxt
```

## Examples

✅ Good:

* `sql_query_plaintxt`
* `logs_plaintxt`

---

# 23) QComboBox

## Exact form

```text id="0j9wd6"
<selected_meaning>_combo
```

## Examples

✅ Good:

* `role_combo`
* `category_combo`
* `supplier_combo`
* `status_combo`

❌ Bad:

* `combobox1`
* `dropdown`

---

# 24) QCheckBox

## Exact form

```text id="zv4s81"
<boolean_meaning>_checkbox
```

## Examples

✅ Good:

* `remember_me_checkbox`
* `active_checkbox`
* `track_stock_checkbox`

❌ Bad:

* `check1`
* `active_state_checkbox`

---

# 25) QRadioButton

## Exact form

```text id="g2mhzw"
<option_meaning>_radiobtn
```

## Examples

✅ Good:

* `male_radiobtn`
* `female_radiobtn`
* `cash_radiobtn`
* `credit_radiobtn`

---

# 26) QFrame

## Exact form

```text id="b4uh77"
<section_meaning>_frame
```

## Examples

✅ Good:

* `login_form_frame`
* `header_frame`
* `sidebar_frame`
* `filters_frame`
* `summary_frame`

❌ Bad:

* `frame1`
* `left_frame`

> Use position only if it is really necessary.

---

# 27) QWidget

## Exact form

```text id="8y4vq3"
<section_meaning>_widget
```

## Examples

✅ Good:

* `profile_widget`
* `stats_widget`
* `details_widget`

---

# 28) QGroupBox

## Exact form

```text id="mkylv3"
<group_meaning>_group
```

## Examples

✅ Good:

* `client_info_group`
* `price_group`
* `filters_group`

---

# 29) QTableWidget / QTableView

## Exact form

```text id="p6rm5z"
<data_meaning>_table
```

## Examples

✅ Good:

* `article_table`
* `invoice_table`
* `supplier_table`
* `stock_table`

❌ Bad:

* `table1`
* `main_table`
* `data_table`

---

# 30) QListWidget / QListView

## Exact form

```text id="26qzpo"
<data_meaning>_list
```

## Examples

✅ Good:

* `notifications_list`
* `clients_list`
* `results_list`

---

# 31) QTreeWidget / QTreeView

## Exact form

```text id="7kdfh3"
<data_meaning>_tree
```

## Examples

✅ Good:

* `categories_tree`
* `permissions_tree`
* `folders_tree`

---

# 32) QTabWidget

## Exact form

```text id="d8zshq"
<section_meaning>_tabs
```

## Examples

✅ Good:

* `settings_tabs`
* `reports_tabs`
* `invoice_tabs`

---

# 33) QSpinBox

## Exact form

```text id="78g2ns"
<value_meaning>_spinbox
```

## Examples

✅ Good:

* `quantity_spinbox`
* `stock_spinbox`
* `age_spinbox`

---

# 34) QDoubleSpinBox

## Exact form

```text id="k3s7f0"
<value_meaning>_doublespinbox
```

## Examples

✅ Good:

* `price_doublespinbox`
* `discount_doublespinbox`
* `weight_doublespinbox`

---

# 35) QDateEdit

## Exact form

```text id="9f57rk"
<date_meaning>_dateedit
```

## Examples

✅ Good:

* `invoice_date_dateedit`
* `delivery_date_dateedit`
* `birth_date_dateedit`

---

# 36) QDateTimeEdit

## Exact form

```text id="lkjw2t"
<datetime_meaning>_datetimeedit
```

## Examples

✅ Good:

* `created_at_datetimeedit`
* `updated_at_datetimeedit`

---

# 37) QTimeEdit

## Exact form

```text id="6j4mti"
<time_meaning>_timeedit
```

## Examples

✅ Good:

* `start_time_timeedit`
* `end_time_timeedit`

---

# 38) QCalendarWidget

## Exact form

```text id="2nukl0"
<calendar_meaning>_calendar
```

## Examples

✅ Good:

* `invoice_calendar`
* `schedule_calendar`

---

# 39) QProgressBar

## Exact form

```text id="q6l2u8"
<progress_meaning>_progressbar
```

## Examples

✅ Good:

* `loading_progressbar`
* `upload_progressbar`

---

# 40) QSlider

## Exact form

```text id="h55zcc"
<value_meaning>_slider
```

## Examples

✅ Good:

* `volume_slider`
* `zoom_slider`

---

# 41) QScrollArea

## Exact form

```text id="40ax6c"
<section_meaning>_scrollarea
```

## Examples

✅ Good:

* `products_scrollarea`
* `history_scrollarea`

---

# 42) QStackedWidget

## Exact form

```text id="0zgjf4"
<section_meaning>_stacked
```

## Examples

✅ Good:

* `auth_stacked`
* `main_content_stacked`

---

# 43) QToolButton

## Exact form

```text id="vx4z2c"
<action>_toolbtn
```

## Examples

✅ Good:

* `close_toolbtn`
* `settings_toolbtn`
* `refresh_toolbtn`

---

# 44) QAction

## Exact form

```text id="u5it5v"
<action>_action
```

## Examples

✅ Good:

* `save_action`
* `export_pdf_action`
* `logout_action`

---

# 45) How to Make Widget Names Unique

Inside the same window, no two widgets may have the same name.

## Exact expansion order

If a widget name is not unique, expand it in this order:

### Level 1

```text id="8q7hnh"
<purpose>_<type>
```

Example:

* `save_btn`

### Level 2

```text id="qv5u86"
<context>_<purpose>_<type>
```

Example:

* `article_save_btn`

### Level 3

```text id="v4i1wv"
<section>_<context>_<purpose>_<type>
```

Example:

* `header_article_save_btn`

## Rule

Use the **shortest unique valid name**.

---

# 46) Recommended Full Example (Login Window)

## Folder

```text id="4u7q0v"
login/
```

## Files

```text id="x39g5j"
login.ui
login.py
login_funcs.py
```

## Class

```python id="eg5j5r"
class LoginWindow:
    ...
```

## Widgets

```text id="lh3s4m"
username_entry
password_entry
login_btn
connection_error_lbl
remember_me_checkbox
login_form_frame
```

## Functions

```python id="x2t70m"
authenticate_user()
check_user()
validate_password()
on_login_btn_clicked()
```

---

# 47) Final Rule

If a new item does not fit one of the exact forms in this document,
you can generate one but it must be like these ones, I think you get the Naming method, so you can deal with the rare and unmentioned cases.

Naming is part of the architecture.

````

---

## 1)
**Files / funcs / widgets / variables** = `snake_case`

## 2)
**Classes** = `PascalCase`

## 3)
**Every widget name must be**
```text
<purpose>_<type>
````

---

## **“Forbidden Names”**


* `pushButton`
* `label1`
* `frame2`
* `widget`
* `main_frame`
* `test.py`
* `helpers.py`
* `tmp`