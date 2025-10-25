import { Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Record from './pages/Record';
import Report from './pages/Report';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/record" element={<Record />} />
      <Route path="/report" element={<Report />} />
    </Routes>
  );
}

export default App;
