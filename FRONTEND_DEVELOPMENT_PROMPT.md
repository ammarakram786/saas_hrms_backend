# HRMS Frontend Development Prompt

## Project Overview
Build a modern, responsive Human Resource Management System (HRMS) frontend using **Nuxt 3** and **PrimeVue**. This is a comprehensive HR management application with employee management, attendance tracking, leave management, payroll processing, and audit logging capabilities.

## Technology Stack
- **Framework**: Nuxt 3 (Vue 3 Composition API)
- **UI Library**: PrimeVue 3.x
- **Styling**: PrimeVue themes + custom CSS
- **State Management**: Pinia
- **HTTP Client**: $fetch (Nuxt 3 built-in)
- **Authentication**: JWT tokens
- **Icons**: PrimeIcons
- **Charts**: Chart.js or similar
- **Date Handling**: Day.js or date-fns

## Backend API Base URL
```
http://localhost:8000/api/v1
```

## Authentication System

### JWT Token Management
- Store access and refresh tokens in secure HTTP-only cookies
- Implement automatic token refresh
- Handle token expiration gracefully
- Redirect to login on authentication failure

### User Roles & Permissions
- **Superuser**: Full access to all features
- **Admin**: Most features except superuser management
- **Manager**: Employee and attendance management
- **Employee**: Self-service features only

## Core Features & Pages

### 1. Authentication Pages

#### Login Page (`/login`)
```vue
<template>
  <div class="login-container">
    <Card class="login-card">
      <template #title>HRMS Login</template>
      <template #content>
        <form @submit.prevent="handleLogin">
          <div class="field">
            <label for="email">Email</label>
            <InputText id="email" v-model="form.email" type="email" required />
          </div>
          <div class="field">
            <label for="password">Password</label>
            <Password id="password" v-model="form.password" required />
          </div>
          <Button type="submit" label="Login" :loading="loading" />
        </form>
      </template>
    </Card>
  </div>
</template>
```

#### Register Page (`/register`)
- User registration form
- Password confirmation
- Terms acceptance
- Redirect to login after successful registration

#### Accept Invitation Page (`/accept-invitation`)
- Token-based invitation acceptance
- User details form
- Password setup
- Role assignment display

### 2. Dashboard (`/dashboard`)

#### Main Dashboard Layout
```vue
<template>
  <div class="dashboard">
    <Menubar :model="menuItems" />
    <div class="content">
      <router-view />
    </div>
  </div>
</template>
```

#### Dashboard Cards
- **Employee Statistics**: Total, Active, New Hires
- **Attendance Overview**: Today's attendance, late arrivals
- **Leave Requests**: Pending approvals
- **Recent Activities**: Audit log entries
- **Quick Actions**: Clock in/out, Create employee, etc.

#### Charts & Analytics
- Employee distribution by department
- Attendance trends (monthly/weekly)
- Leave balance overview
- Payroll summary

### 3. Employee Management (`/employees`)

#### Employee List Page
```vue
<template>
  <div class="employee-list">
    <DataTable 
      :value="employees" 
      :paginator="true" 
      :rows="20"
      :filters="filters"
      filterDisplay="row"
      :loading="loading"
    >
      <template #header>
        <div class="flex justify-between">
          <h2>Employees</h2>
          <Button label="Add Employee" icon="pi pi-plus" @click="showCreateDialog" />
        </div>
      </template>
      
      <Column field="employee_id" header="ID" sortable />
      <Column field="full_name" header="Name" sortable />
      <Column field="email" header="Email" sortable />
      <Column field="department" header="Department" sortable />
      <Column field="position" header="Position" sortable />
      <Column field="status" header="Status" sortable>
        <template #body="{ data }">
          <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
        </template>
      </Column>
      <Column header="Actions">
        <template #body="{ data }">
          <Button icon="pi pi-eye" class="p-button-text" @click="viewEmployee(data)" />
          <Button icon="pi pi-pencil" class="p-button-text" @click="editEmployee(data)" />
          <Button icon="pi pi-trash" class="p-button-text" @click="deleteEmployee(data)" />
        </template>
      </Column>
    </DataTable>
  </div>
</template>
```

#### Employee Form (Create/Edit)
- **Personal Information**: Name, email, phone, DOB, gender, etc.
- **Address**: Street, city, state, postal code, country
- **Employment**: Department, position, employment type, hire date
- **Salary**: Base salary, currency, pay frequency
- **Manager**: Dropdown selection
- **Emergency Contact**: JSON field with contact details
- **Skills & Certifications**: JSON arrays
- **Documents**: File upload for employee documents

#### Employee Detail Page (`/employees/:id`)
- **Personal Information Tab**
- **Employment Details Tab**
- **Attendance History Tab**
- **Leave Records Tab**
- **Documents Tab**
- **Performance Tab**

#### Advanced Filtering
- Search by name, email, employee ID
- Filter by department, status, employment type
- Date range filters (hire date, etc.)
- Salary range filters
- Manager hierarchy filters

### 4. Department Management (`/departments`)

#### Department List
- Department name, code, description
- Employee count per department
- Budget information
- Parent department hierarchy
- Department head assignment

#### Department Form
- Basic information (name, code, description)
- Parent department selection
- Department head assignment
- Budget and cost center
- Active status toggle

### 5. Attendance Management (`/attendance`)

#### Attendance Dashboard
- **Today's Overview**: Present, absent, late, on leave
- **Clock In/Out**: Quick action buttons
- **Recent Attendance**: Last 7 days
- **Attendance Calendar**: Monthly view with status indicators

#### Attendance List
```vue
<template>
  <DataTable :value="attendanceRecords" :paginator="true" :rows="20">
    <Column field="employee.full_name" header="Employee" sortable />
    <Column field="date" header="Date" sortable />
    <Column field="check_in" header="Check In" sortable />
    <Column field="check_out" header="Check Out" sortable />
    <Column field="hours_worked" header="Hours" sortable />
    <Column field="status" header="Status" sortable>
      <template #body="{ data }">
        <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
      </template>
    </Column>
    <Column field="overtime_hours" header="Overtime" sortable />
  </DataTable>
</template>
```

#### Clock In/Out Interface
- **Current Status**: Show if already clocked in/out
- **Time Display**: Current time
- **Quick Actions**: Clock in, clock out, break
- **Notes**: Optional notes for attendance
- **Shift Selection**: If multiple shifts available

#### Attendance Reports
- **Daily Report**: Attendance for specific date
- **Monthly Report**: Attendance summary by month
- **Employee Report**: Individual attendance history
- **Department Report**: Department-wise attendance
- **Export Options**: PDF, Excel export

### 6. Leave Management (`/leave`)

#### Leave Dashboard
- **Leave Balance**: Available leave days by type
- **Pending Requests**: Requests awaiting approval
- **Upcoming Leaves**: Approved leaves in next 30 days
- **Leave Calendar**: Monthly view of all leaves

#### Leave Request Form
```vue
<template>
  <form @submit.prevent="submitLeaveRequest">
    <div class="grid">
      <div class="col-12 md:col-6">
        <div class="field">
          <label>Leave Type</label>
          <Dropdown v-model="form.leave_type" :options="leaveTypes" optionLabel="name" />
        </div>
      </div>
      <div class="col-12 md:col-3">
        <div class="field">
          <label>Start Date</label>
          <Calendar v-model="form.start_date" dateFormat="yy-mm-dd" />
        </div>
      </div>
      <div class="col-12 md:col-3">
        <div class="field">
          <label>End Date</label>
          <Calendar v-model="form.end_date" dateFormat="yy-mm-dd" />
        </div>
      </div>
      <div class="col-12">
        <div class="field">
          <label>Reason</label>
          <Textarea v-model="form.reason" rows="4" />
        </div>
      </div>
    </div>
    <Button type="submit" label="Submit Request" />
  </form>
</template>
```

#### Leave Types Management
- Leave type configuration
- Days allowed per year
- Paid/unpaid status
- Approval requirements
- Gender-specific leaves

#### Leave Approval Interface
- **Pending Requests**: List of requests awaiting approval
- **Request Details**: Full request information
- **Approval Actions**: Approve, reject with reason
- **Bulk Actions**: Approve/reject multiple requests

#### Leave Balance Tracking
- **Current Balance**: Available days by leave type
- **Used Days**: Days taken this year
- **Pending Days**: Days in pending requests
- **Carry Forward**: Previous year's unused days

### 7. Payroll Management (`/payroll`)

#### Payroll Dashboard
- **Current Period**: Active payroll period
- **Processing Status**: Draft, processing, completed
- **Total Employees**: Count of employees in payroll
- **Total Amount**: Gross and net payroll amounts

#### Payroll Periods
- **Period List**: All payroll periods
- **Create Period**: New payroll period setup
- **Process Payroll**: Calculate and process payroll
- **Period Details**: Detailed period information

#### Payroll Records
```vue
<template>
  <DataTable :value="payrollRecords" :paginator="true" :rows="20">
    <Column field="employee.full_name" header="Employee" sortable />
    <Column field="payroll_period.name" header="Period" sortable />
    <Column field="base_salary" header="Base Salary" sortable />
    <Column field="overtime_pay" header="Overtime" sortable />
    <Column field="allowances" header="Allowances" sortable />
    <Column field="gross_pay" header="Gross Pay" sortable />
    <Column field="total_deductions" header="Deductions" sortable />
    <Column field="net_pay" header="Net Pay" sortable />
  </DataTable>
</template>
```

#### Payroll Components
- **Earnings**: Base salary, overtime, allowances, bonuses
- **Deductions**: Tax, social security, other deductions
- **Component Management**: Create, edit, delete components
- **Calculation Methods**: Fixed amount, percentage, formula

#### Payslip Generation
- **Individual Payslips**: Generate for specific employee
- **Bulk Generation**: Generate all payslips for period
- **PDF Export**: Download payslip as PDF
- **Email Distribution**: Send payslips via email

### 8. User Management (`/users`)

#### User List
- User information with roles
- Active/inactive status
- Last login information
- Role assignments

#### User Form
- **Basic Information**: Name, email, password
- **Role Assignment**: Multiple role selection
- **Permissions**: Effective permissions display
- **Account Status**: Active/inactive toggle

#### Role Management
- **Role List**: All available roles
- **Role Form**: Create/edit roles
- **Permission Assignment**: Assign permissions to roles
- **Role Hierarchy**: Role relationships

#### Invitation System
- **Send Invitations**: Invite new users
- **Invitation List**: Track sent invitations
- **Resend Invitations**: Resend expired invitations
- **Invitation Status**: Pending, accepted, expired

### 9. Audit & Reports (`/audit`)

#### Audit Log
```vue
<template>
  <DataTable :value="auditLogs" :paginator="true" :rows="20">
    <Column field="actor_username" header="User" sortable />
    <Column field="action" header="Action" sortable />
    <Column field="model_name" header="Model" sortable />
    <Column field="description" header="Description" sortable />
    <Column field="created_at" header="Date" sortable />
  </DataTable>
</template>
```

#### Report Generation
- **Employee Reports**: Employee lists, directories
- **Attendance Reports**: Daily, monthly, yearly
- **Leave Reports**: Leave summaries, balances
- **Payroll Reports**: Payroll summaries, tax reports
- **Custom Reports**: Configurable report builder

### 10. Settings (`/settings`)

#### System Settings
- **Company Information**: Name, address, contact details
- **Holiday Calendar**: Company holidays
- **Work Shifts**: Shift definitions and schedules
- **Leave Policies**: Leave type configurations

#### User Preferences
- **Profile Settings**: Personal information update
- **Password Change**: Change user password
- **Notification Settings**: Email preferences
- **Theme Settings**: UI theme selection

## API Integration

### HTTP Client Setup
```javascript
// composables/useApi.js
export const useApi = () => {
  const config = useRuntimeConfig()
  
  const api = $fetch.create({
    baseURL: config.public.apiBase,
    onRequest({ request, options }) {
      // Add auth token
      const token = useCookie('access_token')
      if (token.value) {
        options.headers = {
          ...options.headers,
          Authorization: `Bearer ${token.value}`
        }
      }
    },
    onResponseError({ response }) {
      if (response.status === 401) {
        // Handle token expiration
        navigateTo('/login')
      }
    }
  })
  
  return { api }
}
```

### State Management (Pinia)
```javascript
// stores/auth.js
export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(null)
  
  const login = async (credentials) => {
    const { api } = useApi()
    const response = await api('/auth/login/', {
      method: 'POST',
      body: credentials
    })
    
    user.value = response.user
    token.value = response.access_token
    
    // Set cookies
    const accessToken = useCookie('access_token')
    const refreshToken = useCookie('refresh_token')
    accessToken.value = response.access_token
    refreshToken.value = response.refresh_token
  }
  
  const logout = async () => {
    const { api } = useApi()
    await api('/auth/logout/', { method: 'POST' })
    
    user.value = null
    token.value = null
    
    // Clear cookies
    const accessToken = useCookie('access_token')
    const refreshToken = useCookie('refresh_token')
    accessToken.value = null
    refreshToken.value = null
  }
  
  return { user, token, login, logout }
})
```

## UI/UX Requirements

### Design System
- **Color Scheme**: Professional blue/gray palette
- **Typography**: Clean, readable fonts
- **Spacing**: Consistent spacing using PrimeVue's grid system
- **Icons**: PrimeIcons for consistency
- **Components**: Use PrimeVue components throughout

### Responsive Design
- **Mobile First**: Design for mobile, enhance for desktop
- **Breakpoints**: 
  - Mobile: < 768px
  - Tablet: 768px - 1024px
  - Desktop: > 1024px
- **Navigation**: Collapsible sidebar for mobile

### Accessibility
- **Keyboard Navigation**: Full keyboard support
- **Screen Reader**: Proper ARIA labels
- **Color Contrast**: WCAG AA compliance
- **Focus Management**: Clear focus indicators

### Performance
- **Lazy Loading**: Load components on demand
- **Image Optimization**: Optimize images for web
- **Caching**: Implement proper caching strategies
- **Bundle Size**: Keep bundle size minimal

## Data Tables & Filtering

### Advanced Filtering
All data tables should include:
- **Search**: Global search across multiple fields
- **Column Filters**: Individual column filtering
- **Date Range**: Date picker for date fields
- **Dropdown Filters**: For status, department, etc.
- **Sorting**: Multi-column sorting
- **Pagination**: Server-side pagination with configurable page sizes

### Export Functionality
- **CSV Export**: Export filtered data as CSV
- **PDF Export**: Generate PDF reports
- **Excel Export**: Export to Excel format
- **Print**: Print-friendly views

## Error Handling

### Global Error Handling
```javascript
// plugins/error-handler.client.js
export default defineNuxtPlugin(() => {
  const { $toast } = useNuxtApp()
  
  // Handle unhandled errors
  window.addEventListener('unhandledrejection', (event) => {
    $toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'An unexpected error occurred',
      life: 3000
    })
  })
})
```

### Form Validation
- **Client-side**: Real-time validation feedback
- **Server-side**: Display server validation errors
- **Custom Validators**: Business logic validation
- **Error Messages**: Clear, actionable error messages

## Security Considerations

### Authentication
- **JWT Tokens**: Secure token storage
- **Token Refresh**: Automatic token renewal
- **Session Management**: Proper session handling
- **Logout**: Clear all user data on logout

### Authorization
- **Route Guards**: Protect routes based on permissions
- **Component Guards**: Show/hide components based on roles
- **API Security**: Secure API communication
- **Data Protection**: Protect sensitive data

## Testing Requirements

### Unit Tests
- Test individual components
- Test composables and utilities
- Test store actions and mutations
- Test API integration functions

### Integration Tests
- Test complete user flows
- Test API integration
- Test authentication flows
- Test form submissions

### E2E Tests
- Test critical user journeys
- Test cross-browser compatibility
- Test responsive design
- Test accessibility features

## Deployment Considerations

### Environment Configuration
```javascript
// nuxt.config.ts
export default defineNuxtConfig({
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1'
    }
  }
})
```

### Build Optimization
- **Code Splitting**: Automatic code splitting
- **Tree Shaking**: Remove unused code
- **Asset Optimization**: Optimize images and assets
- **CDN**: Use CDN for static assets

## File Structure
```
src/
├── components/
│   ├── common/
│   ├── forms/
│   ├── tables/
│   └── charts/
├── composables/
│   ├── useApi.js
│   ├── useAuth.js
│   └── usePermissions.js
├── layouts/
│   ├── default.vue
│   └── auth.vue
├── pages/
│   ├── index.vue
│   ├── login.vue
│   ├── dashboard/
│   ├── employees/
│   ├── attendance/
│   ├── leave/
│   ├── payroll/
│   └── settings/
├── stores/
│   ├── auth.js
│   ├── employees.js
│   └── attendance.js
├── utils/
│   ├── formatters.js
│   ├── validators.js
│   └── constants.js
└── assets/
    ├── styles/
    └── images/
```

## API Endpoints Reference

### Authentication
- `POST /auth/login/` - User login
- `POST /auth/logout/` - User logout
- `POST /auth/register/` - User registration
- `POST /auth/refresh-token/` - Refresh access token
- `GET /auth/permissions/` - Get user permissions
- `POST /auth/accept-invitation/` - Accept invitation
- `POST /auth/assign-role/` - Assign role to user

### Users
- `GET /auth/users/` - List users
- `POST /auth/users/` - Create user
- `GET /auth/users/{id}/` - Get user details
- `PUT /auth/users/{id}/` - Update user
- `DELETE /auth/users/{id}/` - Delete user
- `POST /auth/users/{id}/assign_roles/` - Assign roles

### Roles
- `GET /auth/roles/` - List roles
- `POST /auth/roles/` - Create role
- `PUT /auth/roles/{id}/` - Update role
- `DELETE /auth/roles/{id}/` - Delete role

### Invitations
- `GET /auth/invitations/` - List invitations
- `POST /auth/invitations/` - Create invitation
- `PUT /auth/invitations/{id}/` - Update invitation
- `DELETE /auth/invitations/{id}/` - Delete invitation
- `POST /auth/invitations/{id}/resend/` - Resend invitation

### Employees
- `GET /employees/employees/` - List employees
- `POST /employees/employees/` - Create employee
- `GET /employees/employees/{id}/` - Get employee details
- `PUT /employees/employees/{id}/` - Update employee
- `DELETE /employees/employees/{id}/` - Delete employee
- `POST /employees/employees/{id}/terminate/` - Terminate employee
- `POST /employees/employees/{id}/reactivate/` - Reactivate employee
- `GET /employees/employees/{id}/hierarchy/` - Get employee hierarchy
- `GET /employees/employees/{id}/direct_reports/` - Get direct reports
- `GET /employees/employees/statistics/` - Get employee statistics

### Departments
- `GET /employees/departments/` - List departments
- `POST /employees/departments/` - Create department
- `GET /employees/departments/{id}/` - Get department details
- `PUT /employees/departments/{id}/` - Update department
- `DELETE /employees/departments/{id}/` - Delete department
- `GET /employees/departments/{id}/employees/` - Get department employees
- `GET /employees/departments/statistics/` - Get department statistics

### Attendance
- `GET /attendance/attendance/` - List attendance records
- `POST /attendance/attendance/` - Create attendance record
- `GET /attendance/attendance/{id}/` - Get attendance details
- `PUT /attendance/attendance/{id}/` - Update attendance
- `DELETE /attendance/attendance/{id}/` - Delete attendance
- `GET /attendance/attendance/statistics/` - Get attendance statistics
- `POST /employees/attendance/clock-in/` - Clock in
- `POST /employees/attendance/clock-out/` - Clock out

### Leave Management
- `GET /attendance/leave-types/` - List leave types
- `POST /attendance/leave-types/` - Create leave type
- `GET /attendance/leave-balances/` - List leave balances
- `POST /attendance/leave-balances/` - Create leave balance
- `GET /attendance/leave-requests/` - List leave requests
- `POST /attendance/leave-requests/` - Create leave request
- `POST /attendance/leave-requests/{id}/approve/` - Approve leave request
- `POST /attendance/leave-requests/{id}/reject/` - Reject leave request

### Payroll
- `GET /payroll/periods/` - List payroll periods
- `POST /payroll/periods/` - Create payroll period
- `GET /payroll/records/` - List payroll records
- `POST /payroll/records/` - Create payroll record
- `GET /payroll/components/` - List payroll components
- `POST /payroll/components/` - Create payroll component

### Audit
- `GET /audit/logs/` - List audit logs

## Query Parameters for Filtering

### Common Parameters
- `search` - Global search term
- `ordering` - Sort by field (prefix with - for descending)
- `page` - Page number
- `per_page` - Items per page (default: 20, max: 100)

### Employee Filters
- `status` - Employee status (active, inactive, terminated, on_leave)
- `employment_type` - Employment type (full_time, part_time, contract, intern, temporary)
- `department` - Department name
- `hire_date_from` - Hire date from
- `hire_date_to` - Hire date to
- `base_salary_min` - Minimum base salary
- `base_salary_max` - Maximum base salary

### Attendance Filters
- `date_from` - Date from
- `date_to` - Date to
- `status` - Attendance status (present, absent, late, half_day, on_leave)
- `employee` - Employee ID
- `department` - Department name

### Leave Request Filters
- `status` - Request status (pending, approved, rejected, cancelled)
- `start_date_from` - Start date from
- `start_date_to` - Start date to
- `employee` - Employee ID
- `leave_type` - Leave type ID

## Response Format

All API responses follow this format:
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "count": 150,
    "next": "http://api/employees/?page=3",
    "previous": "http://api/employees/?page=1",
    "current_page": 2,
    "total_pages": 8,
    "page_size": 20,
    "has_next": true,
    "has_previous": true
  }
}
```

## Error Response Format

```json
{
  "success": false,
  "errors": {
    "field_name": ["Error message 1", "Error message 2"]
  },
  "message": "Validation failed"
}
```

This comprehensive prompt provides everything needed to build a modern, professional HRMS frontend using Nuxt 3 and PrimeVue. The backend is fully REST API-based with comprehensive filtering, pagination, and role-based access control.
