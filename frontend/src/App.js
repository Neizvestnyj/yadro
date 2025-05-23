import {BrowserRouter as Router, Route, Routes} from 'react-router-dom';
import MainPage from './components/MainPage';
import UserPage from './components/UserPage';
import RandomUserPage from './components/RandomUserPage';
import {Container} from 'react-bootstrap';

/**
 * Главный компонент приложения с маршрутизацией.
 *
 * :returns: JSX элемент приложения.
 * :rtype: JSX.Element
 */
function App() {
    return (
        <Router>
            <Container className="mt-4">
                <Routes>
                    <Route path="/" element={<MainPage/>}/>
                    <Route path="/user/:id" element={<UserPage/>}/>
                    <Route path="/random" element={<RandomUserPage/>}/>
                </Routes>
            </Container>
        </Router>
    );
}

export default App;