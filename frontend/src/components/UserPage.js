import {useEffect, useState} from 'react';
import {Link, useParams} from 'react-router-dom';
import axios from 'axios';
import {Button, Card} from 'react-bootstrap';

const UserPage = () => {
    const {id} = useParams();
    const [user, setUser] = useState(null);

    useEffect(() => {
        const fetchUser = async () => {
            try {
                const response = await axios.get(`http://localhost:8000/v1/users/${id}`);
                setUser(response.data);
            } catch (error) {
                console.error('Error fetching user:', error);
            }
        };
        fetchUser();
    }, [id]);

    if (!user) return <div>Loading...</div>;

    return (
        <div>
            <h1>User Details</h1>
            <Card style={{width: '18rem'}}>
                <Card.Img variant="top" src={user.picture}/>
                <Card.Body>
                    <Card.Title>{user.first_name} {user.last_name}</Card.Title>
                    <Card.Text>
                        <strong>Gender:</strong> {user.gender}<br/>
                        <strong>Email:</strong> {user.email}<br/>
                        <strong>Phone:</strong> {user.phone}<br/>
                        <strong>Location:</strong> {user.location}
                    </Card.Text>
                    <Button as={Link} to="/" variant="primary">
                        Back to Main
                    </Button>
                </Card.Body>
            </Card>
        </div>
    );
};

export default UserPage;
