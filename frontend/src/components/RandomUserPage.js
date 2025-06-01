import {useEffect, useState} from 'react';
import axios from 'axios';
import {Button, Card} from 'react-bootstrap';
import {Link} from 'react-router-dom';

const RandomUserPage = () => {
    const [user, setUser] = useState(null);

    useEffect(() => {
        const fetchRandomUser = async () => {
            try {
                const response = await axios.get('http://localhost:8000/api/v1/random');
                setUser(response.data);
            } catch (error) {
                console.error('Error fetching random user:', error);
            }
        };
        fetchRandomUser();
    }, []);

    if (!user) return <div>Loading...</div>;

    return (
        <div>
            <h1>Random User</h1>
            <Card style={{width: '18rem'}}>
                <Card.Img variant="top" src={user.picture}/>
                <Card.Body>
                    <Card.Title>{user.first_name} {user.last_name}</Card.Title>
                    <Card.Text>
                        <strong>Титул:</strong> {user.title}<br/>
                        <strong>Пол:</strong> {user.gender}<br/>
                        <strong>Email:</strong> {user.email}<br/>
                        <strong>Телефон:</strong> {user.phone}<br/>
                        <strong>Мобильный:</strong> {user.cell}<br/>
                        <strong>Адрес:</strong> {user.street_number} {user.street_name}, {user.city}, {user.state}, {user.country}, {user.postcode}<br/>
                        <strong>Координаты:</strong> Широта: {user.latitude}, Долгота: {user.longitude}<br/>
                        <strong>Часовой пояс:</strong> {user.timezone_offset}<br/>
                        <strong>Внешний ID:</strong> {user.external_id}<br/>
                        <strong>Имя пользователя:</strong> {user.username}<br/>
                        <strong>UUID:</strong> {user.uuid}<br/>
                        <strong>Дата рождения:</strong> {new Date(user.dob).toLocaleDateString()}<br/>
                        <strong>Дата регистрации:</strong> {new Date(user.registered_at).toLocaleDateString()}<br/>
                        <strong>Национальность:</strong> {user.nat}<br/>
                        <strong>ID:</strong> {user.id}<br/>
                        <strong>Создано:</strong> {new Date(user.created_at).toLocaleDateString()}
                    </Card.Text>
                    <Button as={Link} to="/" variant="primary" className="me-2">
                        Назад
                    </Button>
                    <Button variant="secondary" onClick={() => window.location.reload()}>
                        Обновить
                    </Button>
                </Card.Body>
            </Card>
        </div>
    );
};

export default RandomUserPage;
