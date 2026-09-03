import { AppRouter } from './routes/AppRouter'
import { AuthProvider } from './context/AuthContext'
import { UiProvider } from './i18n/I18nContext'
export default function App() { return <UiProvider><AuthProvider><AppRouter /></AuthProvider></UiProvider> }
