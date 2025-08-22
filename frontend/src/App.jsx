import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import HomeScreen from './components/HomeScreen';
import TargetScreen from './components/TargetScreen';
import ProductScreen from './components/ProductScreen';
import PredictionScreen from './components/PredictionScreen';
import ImageScreen from './components/ImageScreen';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<HomeScreen />} />
          <Route path="/target" element={<TargetScreen />} />
          <Route path="/product" element={<ProductScreen />} />
          <Route path="/prediction" element={<PredictionScreen />} />
          <Route path="/image" element={<ImageScreen />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

