import {Box, Input, Stack, StackSeparator} from "@chakra-ui/react";
import {useState} from "react";
import {Button} from "@chakra-ui/react";

const LoginForm = props => {
    const {handleSubmit} = props;
    const handleInputChange = (e) => {
        const {name, value} = e.target;
        setFormData((prevData) => ({
            ...prevData, [name]: value,
        }));
    };

    const [formData, setFormData] = useState({
        username: "", password: "",
    })

    return (
        <Box bg={"bg.subtle"}>
            <div className="login-form">
                <form onSubmit={handleSubmit}>
                    <Stack direct ion={{base: "column", md: "row"}} separator={<StackSeparator/>}>
                        <div>
                            <h1>Login</h1>
                        </div>
                        <div>
                            <Input
                                type={"text"}
                                name={"username"}
                                value={formData.username}
                                onChange={handleInputChange}
                            />
                        </div>
                        <div>
                            <Input
                                type={"password"}
                                name={"password"}
                                value={formData.password}
                                onChange={handleInputChange}
                            />
                        </div>
                    </Stack>
                    <Button onClick={() => handleSubmit(formData)}>Login</Button>
                </form>
            </div>
        </Box>
    )
}

export default LoginForm