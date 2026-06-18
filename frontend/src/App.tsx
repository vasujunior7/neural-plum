import { BrowserRouter, Routes, Route } from "react-router-dom"
import { AppShell } from "./components/layout/AppShell"
import { Dashboard } from "./pages/Dashboard"
import { ClaimSubmission } from "./pages/ClaimSubmission"
import { ClaimDetail } from "./pages/ClaimDetail"
function App() {
  return (
    <BrowserRouter>
      <AppShell>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/submit" element={<ClaimSubmission />} />
          <Route path="/claims/:id" element={<ClaimDetail />} />
        </Routes>
      </AppShell>
    </BrowserRouter>
  )
}

export default App
