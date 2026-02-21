namespace targets {
// TODO: Insert the code for the alien class here
class Alien {
public:
    int x_coordinate;
    int y_coordinate;
    Alien(int x, int y, int health = 3) : x_coordinate(x), y_coordinate(y), health(health) {}
    int get_health() {
        return health;
    }
    bool hit() {
        if (health > 0) {
            health--;
            return true;
        }        
        return false;
    }
    bool is_alive() {
        if (health > 0) {
            return true;
        }        
        return false;
    }
    bool teleport(int new_x, int new_y) {
        x_coordinate = new_x;
        y_coordinate = new_y;
        return true;
    }
    bool collision_detection(Alien other) {
        if (x_coordinate == other.x_coordinate && y_coordinate == other.y_coordinate) {
            return true;
        }
        return false;
    }
private:
    int health;
};
}  // namespace targets
