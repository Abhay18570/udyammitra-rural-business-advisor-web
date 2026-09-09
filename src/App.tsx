import { AppRouter } from './routes/AppRouter'
import { AuthProvider } from './context/AuthContext'
import { UiProvider } from './i18n/I18nContext'
export default function App() { return <AuthProvider><UiProvider><AppRouter /></UiProvider></AuthProvider> }
