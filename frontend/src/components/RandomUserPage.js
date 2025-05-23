import {useEffect, useState} from 'react';
import axios from 'axios';
import {Button, Card} from 'react-bootstrap';
import {Link} from 'react-router-dom';

const RandomUserPage = () => {
    const [user, setUser] = useState(null);

    useEffect(() => {
        const fetchRandomUser = async () => {
            try {
                const response = await axios.get('http://localhost:8000/v1/random');
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
                        <strong>Пол:</strong> {user.gender}<br/>
                        <strong>Email:</strong> {user.email}<br/>
                        <strong>Телефон:</strong> {user.phone}<br/>
                        <strong>Местоположение:</strong> {user.location}
                    </Card.Text>
                    <Button as={Link} to="/" variant="primary">
                        Back to Main
                    </Button>
                    <Button variant="secondary" onClick={() => window.location.reload()}>
                        Refresh Random User
                    </Button>
                </Card.Body>
            </Card>
        </div>
    );
};

export default RandomUserPage;
