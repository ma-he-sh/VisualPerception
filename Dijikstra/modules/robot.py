
class Robot():
    def __init__(self, curr_pos, curr_angle, width, height ):
        self.curr_pos   = curr_pos   # robot current pos
        self.curr_angle = curr_angle # robot current angle
        self.width      = width   # robot width
        self.height     = height  # robot height

    def get_robot_outline( self, curr_pos, curr_angle=0 ):
        self.curr_pos   = curr_pos
        self.curr_angle = curr_angle
        
        Xp, Yp = self.curr_pos
        
        """
        x1, y1 ----------- x2, y2
        |           |           |
        |---------Xp, Yp -------|
        |           |           |
        x4, y4 ----------- x3, y3
        """


        x1 = Xp - ( self.width / 2 )
        y1 = Yp + ( self.height / 2 )

        x2 = Xp + ( self.width / 2 )
        y2 = Yp + ( self.height / 2 )

        x3 = Xp + ( self.width / 2 )
        y3 = Yp - ( self.height / 2 )

        x4 = Xp - ( self.width / 2 )
        y4 = Yp - ( self.height / 2 )

        return (x1, y1), (x2, y2), (x3, y3), (x4, y4) 


         

